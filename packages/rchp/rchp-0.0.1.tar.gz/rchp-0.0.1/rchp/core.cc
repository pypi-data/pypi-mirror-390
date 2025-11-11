#define PYBIND11_DETAILED_ERROR_MESSAGES
#include <vector>
#include <thread>
#include <mutex>
#include <atomic>
#include <memory>
#include <queue>
#include <condition_variable>
#include <system_error>
#include <sstream>
#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include "rchp.h"

namespace pb = pybind11;

class Runner {
public:
    explicit Runner(size_t max_workers)
        : alive_(0), stop_(false), added_(0), done_(0) {
        workers_.reserve(max_workers);
    }

    ~Runner() {
        stop_ = true;
        cv_.notify_all();
        for (auto& w : workers_) {
            if (w.joinable()) w.join();
        }
    }

    void add(uintptr_t ptr) {
        if (stop_.load()) {
            throw rchp_error("Runner is shutting down - cannot add new tasks");
        }

        std::lock_guard<std::mutex> lock(mtx_);
        queue_.push(ptr);
        added_++;
        cv_.notify_one();
    }

    void start(size_t count) {
        if (count == 0) {
            throw rchp_error("Cannot start with 0 threads");
        }

        for (size_t i = 0; i < count; ++i) {
            workers_.emplace_back([this, i]() {
                loop(i);
            });
        }
    }

    void wait() {
        std::unique_lock<std::mutex> lock(mtx_);

        stop_ = true;
        cv_.notify_all();

        done_cv_.wait(lock, [this]() {
            bool tasks_done = (done_ >= added_);
            bool workers_idle = (alive_.load() == 0);
            return tasks_done && workers_idle;
        });
    }

    void notify() {
        std::lock_guard<std::mutex> lock(mtx_);
        done_++;

        if (done_ >= added_) {
            done_cv_.notify_one();
        }
    }

private:
    void loop(size_t id) {
        alive_.fetch_add(1);

        while (true) {
            uintptr_t ptr = 0;

            {
                std::unique_lock<std::mutex> lock(mtx_);

                if (done_ >= added_ && stop_.load()) {
                    break;
                }

                cv_.wait(lock, [this]() {
                    return !queue_.empty() || stop_.load();
                });

                if (stop_.load() && queue_.empty()) {
                    break;
                }

                if (!queue_.empty()) {
                    ptr = queue_.front();
                    queue_.pop();
                }
            }

            if (ptr != 0) {
                run(ptr, id);
                notify();
            }
        }

        alive_.fetch_sub(1);

        if (alive_.load() == 0) {
            done_cv_.notify_one();
        }
    }

    void run(uintptr_t ptr, size_t id) {
        PyGILState_STATE state = PyGILState_Ensure();

        try {
            pb::function func = *reinterpret_cast<pb::function*>(ptr);
            func();
        }
        catch (const pb::error_already_set& e) {
            std::string error;
            if (PyErr_Occurred()) {
                PyObject *type, *value, *trace;
                PyErr_Fetch(&type, &value, &trace);

                if (value) {
                    pb::handle h(value);
                    error = pb::str(h);
                } else if (type) {
                    pb::handle h(type);
                    error = pb::str(h);
                } else {
                    error = "Unknown Python error";
                }

                PyErr_Restore(type, value, trace);
            } else {
                error = "Python error_already_set but no active exception";
            }

            PyGILState_Release(state);

            std::stringstream ss;
            ss << "Python exception in worker " << id << ": " << error;
            throw rchp_error(ss.str());
        }
        catch (const std::exception& e) {
            PyGILState_Release(state);
            std::stringstream ss;
            ss << "C++ exception in worker " << id << ": " << e.what();
            throw rchp_error(ss.str());
        }
        catch (...) {
            PyGILState_Release(state);
            std::stringstream ss;
            ss << "Unknown exception in worker " << id;
            throw rchp_error(ss.str());
        }

        PyGILState_Release(state);
    }

    std::vector<std::thread> workers_;
    std::queue<uintptr_t> queue_;
    std::atomic_size_t alive_;
    std::atomic_bool stop_;
    std::atomic_size_t added_;
    std::atomic_size_t done_;

    mutable std::mutex mtx_;
    std::condition_variable cv_;
    std::condition_variable done_cv_;
};

static std::mutex store_mtx;
static std::vector<std::shared_ptr<pb::function>> store;

std::string get_error() {
    if (!PyErr_Occurred()) {
        return "No Python error";
    }

    PyObject *type, *value, *trace;
    PyErr_Fetch(&type, &value, &trace);

    std::string result;

    if (type) {
        pb::handle h(type);
        pb::str s(h);
        result = pb::cast<std::string>(s);
    }

    if (value) {
        pb::handle h(value);
        pb::str s(h);
        result += ": " + pb::cast<std::string>(s);
    }

    PyErr_Restore(type, value, trace);

    return result;
}

void parallel(pb::function func, size_t count, bool wait = false) {
    if (!func) {
        throw rchp_error("Function must be callable");
    }

    if (count == 0) {
        count = std::thread::hardware_concurrency();
        if (count == 0) {
            count = 1;
        }
    }

    auto f_ptr = std::make_shared<pb::function>(func);

    {
        std::lock_guard<std::mutex> lock(store_mtx);
        store.push_back(f_ptr);
    }

    uintptr_t ptr = reinterpret_cast<uintptr_t>(f_ptr.get());

    try {
        if (wait) {
            auto r = std::make_shared<Runner>(count);

            for (size_t i = 0; i < count; ++i) {
                r->add(ptr);
            }

            r->start(count);

            {
                pb::gil_scoped_release release;
                r->wait();
            }

            std::lock_guard<std::mutex> lock(store_mtx);
            store.clear();
        } else {
            for (size_t i = 0; i < count; ++i) {
                std::thread([ptr, f_ptr]() {
                    PyGILState_STATE state = PyGILState_Ensure();
                    try {
                        pb::function func = *reinterpret_cast<pb::function*>(ptr);
                        func();
                    }
                    catch (const pb::error_already_set& e) {
                        std::string error = get_error();
                        std::cerr << "Python exception in thread: " << error << std::endl;
                        PyErr_Clear();
                    }
                    catch (const std::exception& e) {
                        std::cerr << "C++ exception in thread: " << e.what() << std::endl;
                    }
                    catch (...) {
                        std::cerr << "Unknown exception in thread" << std::endl;
                    }
                    PyGILState_Release(state);
                }).detach();
            }
        }
    }
    catch (const std::system_error& e) {
        std::lock_guard<std::mutex> lock(store_mtx);
        store.clear();

        std::stringstream ss;
        ss << "Thread creation failed: " << e.what() << " (code: " << e.code() << ")";
        throw rchp_error(ss.str());
    }
    catch (const rchp_error& e) {
        std::lock_guard<std::mutex> lock(store_mtx);
        store.clear();
        throw;
    }
    catch (const std::exception& e) {
        std::lock_guard<std::mutex> lock(store_mtx);
        store.clear();
        throw rchp_error(std::string("Error: ") + e.what());
    }
    catch (...) {
        std::lock_guard<std::mutex> lock(store_mtx);
        store.clear();
        throw rchp_error("Unknown error in parallel");
    }
}

PYBIND11_MODULE(core, r) {
    pb::register_exception<rchp_error>(r, "rchp_error");
    r.def("parallel", &parallel,
          pb::arg("func"),
          pb::arg("worker"),
          pb::arg("wait") = false);
}
#pragma once

#include "includes.cpp"


int64_t get_available_threads() {
    unsigned int n = std::thread::hardware_concurrency();
    return (n == 0) ? 1 : static_cast<int64_t>(n);
}


template<bool TRACK_COMPLETION = false>
class ThreadPool {
    std::vector<std::thread> workers;
    std::queue<std::function<void()>> tasks;
    std::mutex queue_mutex;
    std::condition_variable condition;
    std::condition_variable wait_condition;
    bool stop;
    int64_t active_tasks;

    int64_t next_task_id = 0;
    std::queue<uint64_t> completed_ids;
    std::mutex completion_mutex;
    std::condition_variable completion_condition;

public:
    explicit ThreadPool(uint64_t parallel) : stop(false), active_tasks(0) {
        if (parallel == 0) parallel = 1;
        for (uint64_t i = 0; i < parallel; ++i) {
            workers.emplace_back([this] {
                while (true) {
                    std::function<void()> task;
                    {
                        std::unique_lock<std::mutex> lock(this->queue_mutex);
                        this->condition.wait(lock, [this] { 
                            return this->stop || !this->tasks.empty(); 
                        });
                        if (this->stop && this->tasks.empty()) {
                            return;
                        }
                        task = std::move(this->tasks.front());
                        this->tasks.pop();
                        this->active_tasks += 1;
                    }
                    task();
                    {
                        std::unique_lock<std::mutex> lock(this->queue_mutex);
                        this->active_tasks -= 1;
                        if (this->active_tasks == 0 && this->tasks.empty()) {
                            this->wait_condition.notify_all();
                        }
                    }
                }
            });
        }
    }

    ~ThreadPool() {
        {
            std::unique_lock<std::mutex> lock(queue_mutex);
            stop = true;
        }
        condition.notify_all();
        for (std::thread& worker : workers) {
            if (worker.joinable()) {
                worker.join();
            }
        }
    }

    template<typename F, typename... Args>
    auto enqueue(F&& f, Args&&... args) -> std::future<std::invoke_result_t<F, Args...>> {
        using return_type = std::invoke_result_t<F, Args...>;
        
        int64_t task_id = next_task_id;
        next_task_id += 1;

        auto task = std::make_shared<std::packaged_task<return_type()>>(
            std::bind(std::forward<F>(f), std::forward<Args>(args)...)
        );

        std::future<return_type> result = task->get_future();
        {
            std::unique_lock<std::mutex> lock(queue_mutex);
            if (stop) {
                throw std::runtime_error("enqueue on stopped ThreadPool");
            }
            if constexpr (TRACK_COMPLETION) {
                tasks.emplace([this, task, task_id]() {
                    (*task)();
                    {
                        std::unique_lock<std::mutex> lock(this->completion_mutex);
                        this->completed_ids.push(task_id);
                    }
                    this->completion_condition.notify_one();
                });
            } else {
                tasks.emplace([task]() { (*task)(); });
            }
        }
        condition.notify_one();
        return result;
    }

    template<bool T = TRACK_COMPLETION>
    std::enable_if_t<T, int64_t> next_completed() {
        std::unique_lock<std::mutex> lock(completion_mutex);
        completion_condition.wait(lock, [this] { 
            return !this->completed_ids.empty(); 
        });
        int64_t task_id = this->completed_ids.front();
        this->completed_ids.pop();
        return task_id;
    }

    void wait() {
        std::unique_lock<std::mutex> lock(queue_mutex);
        wait_condition.wait(lock, [this] {
            return this->tasks.empty() && this->active_tasks == 0;
        });
    }

    ThreadPool(const ThreadPool&) = delete;
    ThreadPool& operator=(const ThreadPool&) = delete;
    ThreadPool(ThreadPool&&) = default;
    ThreadPool& operator=(ThreadPool&&) = default;

};


template<typename T, bool AS_COMPLETED = false>
class ThreadPoolManager : public GeneratorBase<ThreadPoolManager<T, AS_COMPLETED>, T> {
    std::shared_ptr<ThreadPool<AS_COMPLETED>> thread_pool;
    std::unordered_map<int64_t, std::future<T>> futures;
    int64_t next_task_id = 0;
    int64_t last_completed_task_id = -1;

public:
    explicit ThreadPoolManager(int64_t parallel) 
        : thread_pool(std::make_shared<ThreadPool<AS_COMPLETED>>(parallel)) {}

    template<typename F, typename... Args>
    void enqueue(F&& f, Args&&... args) {
        auto future = thread_pool->enqueue(std::forward<F>(f), std::forward<Args>(args)...);
        int64_t task_id = next_task_id;
        next_task_id += 1;
        futures[task_id] = std::move(future);
    }

    std::pair<T, bool> next() {
        if constexpr (AS_COMPLETED) {
            if (futures.empty()) return {{}, true};
            int64_t task_id = thread_pool->next_completed();
            auto it = futures.find(task_id);
            if (it == futures.end()) {
                throw std::runtime_error("internal error: completed task not found");
            }
            auto future = std::move(it->second);
            futures.erase(it);
            T result = future.get();
            return {result, false};
        } else {
            auto it = futures.find(last_completed_task_id + 1);
            if (it == futures.end()) return {{}, true};
            auto future = std::move(it->second);
            futures.erase(it);
            last_completed_task_id += 1;
            T result = future.get();
            return {result, false};
        }
    }

    ThreadPoolManager(const ThreadPoolManager&) = delete;
    ThreadPoolManager& operator=(const ThreadPoolManager&) = delete;
    ThreadPoolManager(ThreadPoolManager&&) = default;
    ThreadPoolManager& operator=(ThreadPoolManager&&) = default;

};


class Semaphore {
    std::mutex mtx;
    std::condition_variable cv;
    int count;

public:
    explicit Semaphore(int initial) : count(initial) {}

    void acquire() {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait(lock, [&] { return count > 0; });
        count -= 1;
    }

    void release() {
        std::unique_lock<std::mutex> lock(mtx);
        count += 1;
        lock.unlock();
        cv.notify_one();
    }

};


class SemaphoreGuard {
    Semaphore& sem;
    bool owns;

public:
    explicit SemaphoreGuard(Semaphore& sem) : sem(sem), owns(true) {
        sem.acquire();
    }

    ~SemaphoreGuard() {
        if (owns) sem.release();
    }

    SemaphoreGuard(const SemaphoreGuard&) = delete;
    SemaphoreGuard& operator=(const SemaphoreGuard&) = delete;
    SemaphoreGuard& operator=(SemaphoreGuard&&) = delete;

    SemaphoreGuard(SemaphoreGuard&& other) noexcept : sem(other.sem), owns(other.owns) {
        other.owns = false;
    }

};

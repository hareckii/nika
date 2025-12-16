#pragma once

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <functional>
#include <thread>
#include <mutex>

class PeriodicService
{
public:
  using Clock = std::chrono::steady_clock;
  using Duration = std::chrono::milliseconds;
  using Task = std::function<void()>;

  PeriodicService();

  void Run(Task task, Duration period) noexcept;

  void Stop() noexcept;

  ~PeriodicService();

private:
  Task m_task;
  Duration m_period;
  std::atomic<bool> m_running;
  std::thread m_worker;
  std::mutex m_mutex;
  std::condition_variable m_cv;

  void RunImpl();
};
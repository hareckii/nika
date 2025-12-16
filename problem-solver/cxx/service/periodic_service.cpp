#include "periodic_service.hpp"

PeriodicService::PeriodicService()
  : m_running(false)
{
}

void PeriodicService::Run(Task task, Duration period) noexcept
{
  m_task = task;
  m_period = period;

  m_running = true;
  m_worker = std::thread(&PeriodicService::RunImpl, this);
}

void PeriodicService::Stop() noexcept
{
  m_running = false;
  m_cv.notify_one();

  if (m_worker.joinable())
    m_worker.join();
}

PeriodicService::~PeriodicService()
{
  Stop();
}

void PeriodicService::RunImpl()
{
  auto next_time = Clock::now() + m_period;
  std::unique_lock<std::mutex> lock(m_mutex);
  while (m_running)
  {
    // Wait until next_time or until Stop() is called
    m_cv.wait_until(
        lock,
        next_time,
        [this]
        {
          return !m_running;
        });
    if (!m_running)
      break;

    lock.unlock();
    m_task();
    lock.lock();

    // Schedule the next invocation, preserving exact cadence
    next_time += m_period;
  }
}
#pragma once

#include <sc-memory/sc_module.hpp>

#include "service/periodic_service.hpp"

class IndexationModule : public ScModule
{
public:
  IndexationModule();

  void Initialize(ScMemoryContext * context) override;

  void Shutdown(ScMemoryContext * context) override;

private:
  PeriodicService m_periodicService;
};
#pragma once

#include <sc-memory/sc_module.hpp>

#include "service/periodic_service.hpp"

class MoodProcessModule : public ScModule
{
public:
  MoodProcessModule();

  void Initialize(ScMemoryContext * context) override;

  void Shutdown(ScMemoryContext * context) override;

private:
  PeriodicService m_periodicService;
};
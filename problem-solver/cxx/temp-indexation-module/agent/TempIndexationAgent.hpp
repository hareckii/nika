#pragma once

#include <sc-memory/sc_agent.hpp>

namespace IndexationModule
{

class TempIndexationAgent : public ScActionInitiatedAgent
{
public:
    explicit TempIndexationAgent(ScMemoryContext * context) : ctx(context) {}

    void DoProgram()
    {
        // Ваша логика индексации или обработки данных
        SC_LOG_DEBUG("TempIndexationAgent executed");
        // Например, поиск и обработка элементов в БЗ
    }

private:
    ScMemoryContext * ctx;
};


}  // namespace IndexationModule

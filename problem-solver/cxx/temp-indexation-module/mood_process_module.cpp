#include "mood_process_module.hpp"

#include "agent/TempIndexationAgent.hpp"
// #include "keynodes/keynodes.hpp"

// SC_MODULE_REGISTER(IndexationModule)->Agent<TempIndexationAgent>();

IndexationModule::IndexationModule() = default;

void IndexationModule::Initialize(ScMemoryContext * context)
{
  m_periodicService.Run(
      [this, context]() -> void
      {
        /*ScMemoryContext context;
        ScTemplate templ;
        templ.Triple(ScType::VarNodeClass >> "_mood", ScType::VarPosArc >> "_mood_arc", Keynodes::myself);
        templ.Quintuple(
            Keynodes::concept_mood, ScType::VarCommonArc, "_mood", ScType::VarPosArc, Keynodes::nrel_inclusion);
        ScTemplateSearchResult result;
        if (context.SearchByTemplate(templ, result))
          context.EraseElement(result[0]["_mood_arc"]);*/
        TempIndexationAgent agent(context);
            // Запускаем агент
        agent.DoProgram();

        
      },
      std::chrono::seconds(5));
}

void IndexationModule::Shutdown(ScMemoryContext * context)
{
  m_periodicService.Stop();
}
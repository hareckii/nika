#include "mood_process_module.hpp"

// #include "agent/mood_define_agent.hpp"
// #include "keynodes/keynodes.hpp"

// SC_MODULE_REGISTER(MoodProcessModule)->Agent<MoodDefineAgent>();

MoodProcessModule::MoodProcessModule() = default;

void MoodProcessModule::Initialize(ScMemoryContext * context)
{
  m_periodicService.Run(
      []() -> void
      {
        ScMemoryContext context;
        ScTemplate templ;
        templ.Triple(ScType::VarNodeClass >> "_mood", ScType::VarPosArc >> "_mood_arc", Keynodes::myself);
        templ.Quintuple(
            Keynodes::concept_mood, ScType::VarCommonArc, "_mood", ScType::VarPosArc, Keynodes::nrel_inclusion);
        ScTemplateSearchResult result;
        if (context.SearchByTemplate(templ, result))
          context.EraseElement(result[0]["_mood_arc"]);
      },
      std::chrono::seconds(5));
}

void MoodProcessModule::Shutdown(ScMemoryContext * context)
{
  m_periodicService.Stop();
}
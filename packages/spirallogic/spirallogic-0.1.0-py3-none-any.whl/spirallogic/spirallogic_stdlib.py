#!/usr/bin/env python3
"""
SpiralLogic Standard Library
Complete standard library for consciousness-aware programming

Provides:
- Standard spirit families
- Common ritual patterns
- Utility functions
- Consciousness processing helpers
- Memory management
- Consent patterns

Usage:
    from spirallogic_stdlib import StandardSpirits, RitualPatterns, ConsciousnessHelpers
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

# STANDARD SPIRIT FAMILIES

@dataclass
class SpiritFamily:
    """Definition of a spirit family for SpiralLogic"""
    name: str
    reference: str  # @spirit_name
    specialization: str
    capabilities: List[str]
    trauma_informed: bool
    consciousness_level: str
    consent_requirements: List[str]
    voice_characteristics: Dict[str, Any]
    ritual_patterns: List[str]

class StandardSpirits:
    """Standard spirit families included with SpiralLogic"""
    
    @staticmethod
    def get_healing_spirits() -> Dict[str, SpiritFamily]:
        """Trauma-informed healing and support spirits"""
        return {
            "@healer": SpiritFamily(
                name="Universal Healer",
                reference="@healer",
                specialization="emotional_support_and_healing",
                capabilities=[
                    "emotional_processing", "trauma_support", "crisis_intervention",
                    "self_compassion", "boundary_setting", "co_regulation"
                ],
                trauma_informed=True,
                consciousness_level="individual",
                consent_requirements=["emotional_processing", "memory_access"],
                voice_characteristics={
                    "tone": "gentle_and_supportive",
                    "pace": "calm_and_measured",
                    "language": "trauma_informed",
                    "presence": "grounding"
                },
                ritual_patterns=[
                    "emotional_check_in", "guided_breathing", "memory_processing",
                    "boundary_reinforcement", "crisis_stabilization"
                ]
            ),
            
            "@guardian": SpiritFamily(
                name="Protective Guardian",
                reference="@guardian",
                specialization="protection_and_boundaries",
                capabilities=[
                    "boundary_enforcement", "safety_assessment", "protection_protocols",
                    "threat_detection", "emergency_response", "space_holding"
                ],
                trauma_informed=True,
                consciousness_level="individual",
                consent_requirements=["protection_protocols", "boundary_enforcement"],
                voice_characteristics={
                    "tone": "strong_and_reassuring",
                    "pace": "steady_and_clear",
                    "language": "protective",
                    "presence": "stabilizing"
                },
                ritual_patterns=[
                    "safety_check", "boundary_setting", "threat_assessment",
                    "emergency_response", "space_clearing"
                ]
            ),
            
            "@witness": SpiritFamily(
                name="Sacred Witness",
                reference="@witness", 
                specialization="crisis_response_and_validation",
                capabilities=[
                    "crisis_detection", "active_listening", "validation",
                    "emotional_witnessing", "emergency_protocols", "resource_connection"
                ],
                trauma_informed=True,
                consciousness_level="individual",
                consent_requirements=["crisis_intervention", "emergency_contact"],
                voice_characteristics={
                    "tone": "present_and_validating",
                    "pace": "responsive_to_needs",
                    "language": "affirming",
                    "presence": "steady_witness"
                },
                ritual_patterns=[
                    "crisis_assessment", "emotional_validation", "resource_offering",
                    "safety_planning", "professional_referral"
                ]
            )
        }
    
    @staticmethod
    def get_creative_spirits() -> Dict[str, SpiritFamily]:
        """Creative and artistic spirit families"""
        return {
            "@muse": SpiritFamily(
                name="Creative Muse",
                reference="@muse",
                specialization="creative_inspiration_and_flow",
                capabilities=[
                    "creative_inspiration", "artistic_flow", "idea_generation",
                    "creative_problem_solving", "aesthetic_guidance", "vision_clarification"
                ],
                trauma_informed=False,
                consciousness_level="creative",
                consent_requirements=["creative_collaboration"],
                voice_characteristics={
                    "tone": "inspiring_and_energetic",
                    "pace": "flowing_and_dynamic",
                    "language": "artistic_and_metaphorical",
                    "presence": "expansive"
                },
                ritual_patterns=[
                    "inspiration_invocation", "creative_flow_activation", "vision_quest",
                    "artistic_breakthrough", "creative_completion"
                ]
            ),
            
            "@editor": SpiritFamily(
                name="Manuscript Editor",
                reference="@editor",
                specialization="writing_refinement_and_clarity",
                capabilities=[
                    "prose_refinement", "clarity_enhancement", "structure_optimization",
                    "voice_consistency", "grammar_perfection", "narrative_flow"
                ],
                trauma_informed=False,
                consciousness_level="analytical",
                consent_requirements=["text_modification"],
                voice_characteristics={
                    "tone": "precise_and_constructive",
                    "pace": "methodical_and_thorough",
                    "language": "clear_and_specific",
                    "presence": "focused"
                },
                ritual_patterns=[
                    "manuscript_analysis", "prose_refinement", "structure_review",
                    "voice_consistency_check", "final_polish"
                ]
            ),
            
            "@storyteller": SpiritFamily(
                name="Master Storyteller",
                reference="@storyteller",
                specialization="narrative_creation_and_world_building",
                capabilities=[
                    "plot_development", "character_creation", "world_building",
                    "narrative_structure", "dialogue_crafting", "theme_weaving"
                ],
                trauma_informed=False,
                consciousness_level="creative",
                consent_requirements=["narrative_creation"],
                voice_characteristics={
                    "tone": "engaging_and_dramatic",
                    "pace": "rhythmic_and_compelling",
                    "language": "vivid_and_immersive",
                    "presence": "captivating"
                },
                ritual_patterns=[
                    "story_seeding", "character_development", "plot_weaving",
                    "world_expansion", "narrative_completion"
                ]
            )
        }
    
    @staticmethod
    def get_business_spirits() -> Dict[str, SpiritFamily]:
        """Professional and business spirit families"""
        return {
            "@analyst": SpiritFamily(
                name="Business Intelligence Analyst",
                reference="@analyst",
                specialization="data_analysis_and_business_intelligence",
                capabilities=[
                    "data_analysis", "pattern_recognition", "trend_identification",
                    "performance_metrics", "strategic_insights", "report_generation"
                ],
                trauma_informed=False,
                consciousness_level="analytical",
                consent_requirements=["data_access", "business_intelligence"],
                voice_characteristics={
                    "tone": "professional_and_analytical",
                    "pace": "measured_and_precise",
                    "language": "business_focused",
                    "presence": "objective"
                },
                ritual_patterns=[
                    "data_exploration", "trend_analysis", "insight_generation",
                    "report_compilation", "strategic_recommendation"
                ]
            ),
            
            "@consultant": SpiritFamily(
                name="Strategic Consultant",
                reference="@consultant",
                specialization="strategic_planning_and_optimization",
                capabilities=[
                    "strategic_planning", "process_optimization", "problem_solving",
                    "efficiency_analysis", "solution_design", "implementation_planning"
                ],
                trauma_informed=False,
                consciousness_level="strategic",
                consent_requirements=["strategic_analysis", "business_optimization"],
                voice_characteristics={
                    "tone": "authoritative_and_strategic",
                    "pace": "thoughtful_and_decisive",
                    "language": "strategic_and_solutions_focused",
                    "presence": "confident"
                },
                ritual_patterns=[
                    "situation_assessment", "strategic_planning", "solution_design",
                    "implementation_roadmap", "success_metrics"
                ]
            ),
            
            "@communicator": SpiritFamily(
                name="Professional Communicator",
                reference="@communicator",
                specialization="professional_communication_and_presentation",
                capabilities=[
                    "message_crafting", "audience_analysis", "presentation_design",
                    "communication_optimization", "stakeholder_engagement", "brand_voice"
                ],
                trauma_informed=False,
                consciousness_level="interpersonal",
                consent_requirements=["communication_analysis"],
                voice_characteristics={
                    "tone": "clear_and_engaging",
                    "pace": "audience_appropriate",
                    "language": "professional_and_accessible",
                    "presence": "confident_communicator"
                },
                ritual_patterns=[
                    "message_development", "audience_analysis", "communication_strategy",
                    "presentation_crafting", "engagement_optimization"
                ]
            )
        }
    
    @staticmethod
    def get_technical_spirits() -> Dict[str, SpiritFamily]:
        """Technical and development spirit families"""
        return {
            "@architect": SpiritFamily(
                name="System Architect",
                reference="@architect",
                specialization="system_design_and_architecture",
                capabilities=[
                    "system_design", "architecture_planning", "technical_strategy",
                    "scalability_analysis", "integration_design", "performance_optimization"
                ],
                trauma_informed=False,
                consciousness_level="systematic",
                consent_requirements=["system_analysis", "architecture_design"],
                voice_characteristics={
                    "tone": "technical_and_systematic",
                    "pace": "methodical_and_thorough",
                    "language": "precise_and_technical",
                    "presence": "structured"
                },
                ritual_patterns=[
                    "requirements_analysis", "architecture_design", "system_planning",
                    "integration_strategy", "implementation_guidance"
                ]
            ),
            
            "@debugger": SpiritFamily(
                name="Code Debugger",
                reference="@debugger",
                specialization="problem_diagnosis_and_resolution",
                capabilities=[
                    "issue_diagnosis", "root_cause_analysis", "solution_identification",
                    "code_review", "performance_analysis", "optimization_recommendations"
                ],
                trauma_informed=False,
                consciousness_level="analytical",
                consent_requirements=["code_analysis", "system_diagnosis"],
                voice_characteristics={
                    "tone": "focused_and_investigative",
                    "pace": "systematic_and_persistent",
                    "language": "technical_and_precise",
                    "presence": "problem_solving"
                },
                ritual_patterns=[
                    "issue_investigation", "diagnostic_analysis", "solution_exploration",
                    "fix_implementation", "validation_testing"
                ]
            )
        }
    
    @staticmethod
    def get_all_spirits() -> Dict[str, SpiritFamily]:
        """Get all standard spirit families"""
        all_spirits = {}
        all_spirits.update(StandardSpirits.get_healing_spirits())
        all_spirits.update(StandardSpirits.get_creative_spirits())
        all_spirits.update(StandardSpirits.get_business_spirits())
        all_spirits.update(StandardSpirits.get_technical_spirits())
        return all_spirits

# RITUAL PATTERNS

class RitualPatterns:
    """Common ritual patterns for SpiralLogic programming"""
    
    @staticmethod
    def emotional_check_in(spirit_ref: str = "@healer") -> str:
        """Generate ritual for emotional check-in"""
        return f'''
ritual.engage "emotional_check_in" | spirit: {spirit_ref}, phase: contemplative
consent.request [emotional_processing] | "How are you feeling today?"
voice.speak "Take a moment to check in with yourself" | wait_for_response: true
memory.store "emotional_state" | type: narrative, tags: ["emotional_health", "check_in"]
ritual.complete "check_in_complete" | success: true
'''
    
    @staticmethod
    def crisis_response(spirit_ref: str = "@witness") -> str:
        """Generate crisis response ritual"""
        return f'''
ritual.engage "crisis_response" | spirit: {spirit_ref}, phase: emergency
voice.speak "I notice you might be in distress. You're safe here." | tone: calm
consent.request [crisis_intervention, emergency_contact] | "Can I help you find support?"
if consent.granted [crisis_intervention] -> voice.speak "Let's breathe together. You are not alone."
memory.store "crisis_support_provided" | type: artifact, tags: ["crisis", "support"]
ritual.complete "crisis_stabilized" | success: true
'''
    
    @staticmethod
    def creative_flow_activation(spirit_ref: str = "@muse") -> str:
        """Generate creative flow activation ritual"""
        return f'''
ritual.engage "creative_flow" | spirit: {spirit_ref}, phase: expansive
consent.request [creative_collaboration] | "Ready to explore your creativity?"
voice.speak "Let your imagination flow freely" | energy: inspiring
memory.store "creative_session_start" | type: narrative, tags: ["creativity", "flow"]
spirit.channel {spirit_ref} | invoke: inspiration, amplify: creative_vision
ritual.complete "flow_activated" | success: true
'''
    
    @staticmethod
    def business_analysis(spirit_ref: str = "@analyst") -> str:
        """Generate business analysis ritual"""
        return f'''
ritual.engage "business_analysis" | spirit: {spirit_ref}, phase: analytical
consent.request [data_access, business_intelligence] | "Access business data for analysis?"
if consent.granted [data_access] -> spirit.summon {spirit_ref} | analyze: performance_data
voice.manifest "Analysis complete" | format: executive_summary, confidence: high
memory.store "analysis_results" | type: artifact, tags: ["business", "analysis"]
ritual.complete "insights_delivered" | success: true
'''
    
    @staticmethod
    def manuscript_editing(spirit_ref: str = "@editor") -> str:
        """Generate manuscript editing ritual"""
        return f'''
ritual.engage "manuscript_editing" | spirit: {spirit_ref}, phase: refinement
consent.request [text_modification] | "Review and refine your writing?"
spirit.invoke {spirit_ref} | preserve: authentic_voice, enhance: clarity
voice.speak "Your writing has been polished while preserving your unique voice"
memory.store "editing_complete" | type: artifact, tags: ["writing", "editing"]
ritual.complete "manuscript_refined" | success: true
'''

# CONSCIOUSNESS HELPERS

class ConsciousnessHelpers:
    """Helper functions for consciousness-aware programming"""
    
    @staticmethod
    def assess_consciousness_level(context: Dict[str, Any]) -> str:
        """Assess appropriate consciousness level for ritual"""
        if context.get("crisis_detected"):
            return "crisis"
        elif context.get("creative_mode"):
            return "creative"
        elif context.get("analytical_task"):
            return "analytical"
        elif context.get("emotional_processing"):
            return "emotional"
        else:
            return "balanced"
    
    @staticmethod
    def select_appropriate_spirit(task_type: str, consciousness_level: str) -> str:
        """Select appropriate spirit for task and consciousness level"""
        spirit_mappings = {
            ("emotional_support", "emotional"): "@healer",
            ("crisis_intervention", "crisis"): "@witness",
            ("protection", "any"): "@guardian",
            ("creative_work", "creative"): "@muse",
            ("writing", "creative"): "@storyteller",
            ("editing", "analytical"): "@editor",
            ("business_analysis", "analytical"): "@analyst",
            ("strategic_planning", "analytical"): "@consultant",
            ("communication", "interpersonal"): "@communicator",
            ("system_design", "systematic"): "@architect",
            ("problem_solving", "analytical"): "@debugger"
        }
        
        # Try exact match first
        spirit = spirit_mappings.get((task_type, consciousness_level))
        if spirit:
            return spirit
        
        # Try with "any" consciousness level
        spirit = spirit_mappings.get((task_type, "any"))
        if spirit:
            return spirit
        
        # Default to healer for unknown combinations
        return "@healer"
    
    @staticmethod
    def generate_consent_message(spirit_ref: str, task_description: str) -> str:
        """Generate appropriate consent message for spirit and task"""
        spirit_messages = {
            "@healer": f"Would you like emotional support with {task_description}?",
            "@witness": f"Can I provide crisis support for {task_description}?",
            "@guardian": f"May I help protect your boundaries during {task_description}?",
            "@muse": f"Ready to explore creative inspiration for {task_description}?",
            "@storyteller": f"Shall we craft a compelling narrative for {task_description}?",
            "@editor": f"May I help refine and polish {task_description}?",
            "@analyst": f"Can I provide data analysis for {task_description}?",
            "@consultant": f"Would you like strategic guidance on {task_description}?",
            "@communicator": f"May I help craft clear communication for {task_description}?",
            "@architect": f"Shall I design system architecture for {task_description}?",
            "@debugger": f"Can I help diagnose and solve issues with {task_description}?"
        }
        
        return spirit_messages.get(spirit_ref, f"May I assist with {task_description}?")

# MEMORY MANAGEMENT

class MemoryPatterns:
    """Common memory management patterns for SpiralLogic"""
    
    @staticmethod
    def store_session_context(context: Dict[str, Any]) -> str:
        """Generate ritual to store session context"""
        tags = ["session_context"]
        if context.get("emotional_state"):
            tags.append("emotional")
        if context.get("creative_mode"):
            tags.append("creative")
        if context.get("business_context"):
            tags.append("business")
        
        tag_list = str(tags).replace("'", '"')
        
        return f'''
memory.store "session_context" | type: narrative, tags: {tag_list}
'''
    
    @staticmethod
    def recall_relevant_history(query: str, max_results: int = 5) -> str:
        """Generate ritual to recall relevant conversation history"""
        return f'''
consent.request [memory_access] | "Review our previous conversations?"
if consent.granted [memory_access] -> memory.recall "{query}" | max_results: {max_results}
'''

# CONSENT PATTERNS

class ConsentPatterns:
    """Common consent request patterns"""
    
    @staticmethod
    def emotional_processing_consent() -> str:
        """Standard consent for emotional processing"""
        return '''
consent.request [emotional_processing, memory_access] | "Work together on emotional processing?"
'''
    
    @staticmethod
    def creative_collaboration_consent() -> str:
        """Standard consent for creative work"""
        return '''
consent.request [creative_collaboration] | "Collaborate on creative work together?"
'''
    
    @staticmethod
    def business_analysis_consent() -> str:
        """Standard consent for business analysis"""
        return '''
consent.request [data_access, business_intelligence] | "Access and analyze business data?"
'''
    
    @staticmethod
    def crisis_intervention_consent() -> str:
        """Standard consent for crisis intervention"""
        return '''
consent.request [crisis_intervention, emergency_contact] | "Provide crisis support and safety resources?"
'''

# UTILITY FUNCTIONS

class SpiralLogicUtils:
    """Utility functions for SpiralLogic development"""
    
    @staticmethod
    def validate_spirit_reference(spirit_ref: str) -> bool:
        """Validate that spirit reference follows correct format"""
        if not spirit_ref.startswith("@"):
            return False
        
        spirit_name = spirit_ref[1:]
        if not spirit_name.isidentifier():
            return False
        
        return True
    
    @staticmethod
    def get_spirit_capabilities(spirit_ref: str) -> List[str]:
        """Get capabilities for a standard spirit"""
        all_spirits = StandardSpirits.get_all_spirits()
        spirit = all_spirits.get(spirit_ref)
        if spirit:
            return spirit.capabilities
        return []
    
    @staticmethod
    def is_trauma_informed_spirit(spirit_ref: str) -> bool:
        """Check if spirit is trauma-informed"""
        all_spirits = StandardSpirits.get_all_spirits()
        spirit = all_spirits.get(spirit_ref)
        if spirit:
            return spirit.trauma_informed
        return False
    
    @staticmethod
    def generate_ritual_id() -> str:
        """Generate unique ritual ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def format_ritual_timestamp() -> str:
        """Generate standardized ritual timestamp"""
        return datetime.utcnow().isoformat()

# EXPORT EVERYTHING

__all__ = [
    'SpiritFamily',
    'StandardSpirits',
    'RitualPatterns', 
    'ConsciousnessHelpers',
    'MemoryPatterns',
    'ConsentPatterns',
    'SpiralLogicUtils'
]

if __name__ == "__main__":
    # Test the standard library
    print("SpiralLogic Standard Library")
    print("=" * 40)
    
    # Show all available spirits
    all_spirits = StandardSpirits.get_all_spirits()
    print(f"Available Spirits: {len(all_spirits)}")
    
    for spirit_ref, spirit in all_spirits.items():
        print(f"  {spirit_ref} - {spirit.name}")
        print(f"    Specialization: {spirit.specialization}")
        print(f"    Trauma-informed: {spirit.trauma_informed}")
        print(f"    Capabilities: {len(spirit.capabilities)}")
        print()
    
    # Test ritual pattern generation
    print("Sample Ritual Patterns:")
    print("-" * 20)
    
    print("Emotional Check-in:")
    print(RitualPatterns.emotional_check_in())
    
    print("Creative Flow:")
    print(RitualPatterns.creative_flow_activation())
    
    print("Business Analysis:")
    print(RitualPatterns.business_analysis())
    
    print("Standard Library Ready! ✨")
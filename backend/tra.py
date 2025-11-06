import json
import networkx as nx
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Set, Optional, Any
from enum import Enum
from pathlib import Path
import os

# ========== CONFIGURATION ==========
JSON_FILE_PATH = Path(__file__).parent.parent / "backend" / "database" / "learning_path.json"

class LearnerType(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate" 
    ADVANCED = "advanced"
    RESEARCHER = "researcher"

class TimeAvailability(Enum):
    PART_TIME = "part_time"    # 5-10 hrs/week
    FULL_TIME = "full_time"    # 20-30 hrs/week  
    INTENSIVE = "intensive"    # 40+ hrs/week

class LearningDomain(Enum):
    AI_ML = "ai_ml"
    WEB_DEV = "web_dev"
    CYBERSECURITY = "cybersecurity"
    CLOUD_COMPUTING = "cloud_computing"
    FULL_STACK = "full_stack"

@dataclass
class LearningNode:
    id: str
    title: str
    type: str
    estimated_time: int
    load: str
    difficulty: int
    prerequisites: List[str] = field(default_factory=list)
    subnodes: List[str] = field(default_factory=list)
    subtopics: List[str] = field(default_factory=list)
    resources: Dict[str, Any] = field(default_factory=dict)
    embedding: List[float] = field(default_factory=list)
    
    def __repr__(self):
        return f"LearningNode({self.id}: {self.title}, {self.estimated_time}hrs)"

class LearningPathGenerator:
    def __init__(self, dataset: List[Dict]):
        self.nodes = self._create_nodes(dataset)
        self.graph = self._build_graph()
        self.main_nodes = [node for node in self.nodes.values() if node.type == "main_node"]
        self.domain_mapping = self._create_domain_mapping()
    
    def _create_domain_mapping(self) -> Dict[LearningDomain, List[str]]:
        """Map learning domains to their main node IDs"""
        return {
            LearningDomain.AI_ML: [
                "foundational_skills", "data_science_core", "machine_learning_fundamentals",
                "deep_learning_specialization", "ai_domains", "production_scale", "ethics_capstone"
            ],
            LearningDomain.WEB_DEV: [
                "web_dev_foundations", "frontend_frameworks", "backend_development",
                "full_stack_integration", "web_dev_capstone"
            ],
            LearningDomain.CYBERSECURITY: [
                "cyber_foundations", "ethical_hacking", "defensive_security",
                "advanced_cyber", "cyber_capstone"
            ],
            LearningDomain.CLOUD_COMPUTING: [
                "cloud_foundations", "aws_core_services", "azure_fundamentals",
                "cloud_architecture", "cloud_devops"
            ],
            LearningDomain.FULL_STACK: []  # Empty means all domains
        }
    
    def _create_nodes(self, dataset: List[Dict]) -> Dict[str, LearningNode]:
        """Create LearningNode objects from dataset with proper error handling"""
        nodes = {}
        for item in dataset:
            try:
                node_data = {
                    'id': item['id'],
                    'title': item['title'],
                    'type': item['type'],
                    'estimated_time': item['estimated_time'],
                    'load': item['load'],
                    'difficulty': item['difficulty'],
                    'prerequisites': item.get('prerequisites', []),
                    'subnodes': item.get('subnodes', []),
                    'subtopics': item.get('subtopics', []),
                    'resources': item.get('resources', {}),
                    'embedding': item.get('embedding', [])
                }
                nodes[item['id']] = LearningNode(**node_data)
            except Exception as e:
                print(f"Error creating node {item.get('id', 'unknown')}: {e}")
                continue
        return nodes
        
    def _build_graph(self) -> nx.DiGraph:
        """Build a directed graph representing prerequisite relationships"""
        G = nx.DiGraph()
        
        for node_id, node in self.nodes.items():
            G.add_node(node_id, **node.__dict__)
            
            for prereq in node.prerequisites:
                if prereq in self.nodes:
                    G.add_edge(prereq, node_id)
            
            for subnode in node.subnodes:
                if subnode in self.nodes:
                    G.add_edge(node_id, subnode)
        
        return G
    
    def calculate_total_available_hours(self, time_availability: TimeAvailability, weeks: int = 12) -> int:
        """Calculate total available hours based on time availability and duration"""
        weekly_hours = {
            TimeAvailability.PART_TIME: 8,    # ~1 day per week
            TimeAvailability.FULL_TIME: 20,   # ~4 days per week  
            TimeAvailability.INTENSIVE: 40    # Full-time
        }
        return weekly_hours[time_availability] * weeks
    
    def get_recommended_path(self, 
                           learner_type: LearnerType,
                           time_availability: TimeAvailability,
                           learning_domain: LearningDomain,
                           study_weeks: int = 12) -> Tuple[List[LearningNode], Dict, Dict]:
        """Generate a personalized learning path based on user profile"""
        
        total_available_hours = self.calculate_total_available_hours(time_availability, study_weeks)
        
        print(f"🎯 Learning Domain: {learning_domain.value.replace('_', ' ').title()}")
        print(f"⏰ Available time: {total_available_hours} hours over {study_weeks} weeks")
        
        # First filter by domain, then by learner type
        domain_filtered_nodes = self._filter_nodes_by_domain(learning_domain)
        filtered_nodes = self._filter_nodes_by_learner_type(learner_type, domain_filtered_nodes)
        
        try:
            topological_order = list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            topological_order = list(self.graph.nodes())
        
        path = []
        completed = set()
        total_time_used = 0
        
        for node_id in topological_order:
            if node_id not in filtered_nodes:
                continue
                
            node = self.nodes[node_id]
            
            prereqs_satisfied = all(prereq in completed for prereq in node.prerequisites)
            
            if prereqs_satisfied and node_id not in completed:
                if total_time_used + node.estimated_time <= total_available_hours:
                    path.append(node)
                    completed.add(node_id)
                    total_time_used += node.estimated_time
                else:
                    continue
        
        weekly_schedule = self._create_weekly_schedule(path, time_availability, study_weeks)
        
        stats = {
            'total_hours_used': total_time_used,
            'total_hours_available': total_available_hours,
            'utilization_percentage': (total_time_used / total_available_hours) * 100,
            'nodes_completed': len(completed),
            'total_nodes': len(filtered_nodes),
            'weeks': study_weeks,
            'hours_per_week': self.calculate_total_available_hours(time_availability, 1),
            'expected_completion': min(study_weeks, round(total_time_used / self.calculate_total_available_hours(time_availability, 1), 1)),
            'learning_domain': learning_domain.value
        }
        
        return path, weekly_schedule, stats
    
    def _filter_nodes_by_domain(self, learning_domain: LearningDomain) -> Set[str]:
        """Filter nodes based on selected learning domain"""
        if learning_domain == LearningDomain.FULL_STACK:
            return set(self.nodes.keys())  # All nodes for full stack
        
        domain_main_nodes = self.domain_mapping[learning_domain]
        domain_nodes = set()
        
        # Add main nodes and all their subnodes recursively
        for main_node_id in domain_main_nodes:
            if main_node_id in self.nodes:
                domain_nodes.add(main_node_id)
                # Add all subnodes recursively
                self._add_subnodes_recursively(main_node_id, domain_nodes)
        
        return domain_nodes
    
    def _add_subnodes_recursively(self, node_id: str, domain_nodes: Set[str]):
        """Recursively add all subnodes of a given node"""
        node = self.nodes.get(node_id)
        if not node:
            return
            
        for subnode_id in node.subnodes:
            if subnode_id in self.nodes and subnode_id not in domain_nodes:
                domain_nodes.add(subnode_id)
                self._add_subnodes_recursively(subnode_id, domain_nodes)
    
    def _filter_nodes_by_learner_type(self, learner_type: LearnerType, node_set: Set[str]) -> Set[str]:
        """Filter nodes based on learner expertise level"""
        difficulty_thresholds = {
            LearnerType.BEGINNER: 4,      # Max difficulty 4
            LearnerType.INTERMEDIATE: 6,  # Max difficulty 6  
            LearnerType.ADVANCED: 8,      # Max difficulty 8
            LearnerType.RESEARCHER: 10    # All nodes
        }
        
        threshold = difficulty_thresholds[learner_type]
        return {node_id for node_id in node_set 
                if self.nodes[node_id].difficulty <= threshold}
    
    def _create_weekly_schedule(self, path: List[LearningNode], 
                              time_availability: TimeAvailability, 
                              total_weeks: int) -> Dict[str, List[LearningNode]]:
        """Create a weekly learning schedule"""
        weekly_hours = {
            TimeAvailability.PART_TIME: 8,
            TimeAvailability.FULL_TIME: 20,
            TimeAvailability.INTENSIVE: 40
        }
        
        schedule = {}
        current_week = 1
        current_week_hours = 0
        current_week_nodes = []
        
        for node in path:
            if current_week_hours + node.estimated_time > weekly_hours[time_availability]:
                if current_week_nodes:
                    schedule[f"Week {current_week}"] = current_week_nodes.copy()
                    current_week += 1
                    current_week_hours = 0
                    current_week_nodes = []
                
                if current_week > total_weeks:
                    break
            
            current_week_nodes.append(node)
            current_week_hours += node.estimated_time
        
        if current_week_nodes and current_week <= total_weeks:
            schedule[f"Week {current_week}"] = current_week_nodes
        
        return schedule

    # ---------------- VISUALIZATION METHODS ----------------

    def visualize_path(self, path: List[LearningNode], stats: Dict):
        """Visualize the learning path with enhanced formatting"""
        print("\n" + "="*80)
        print("🎯 PERSONALIZED LEARNING ROADMAP")
        print("="*80)
        
        print(f"\n📊 STATISTICS:")
        print(f"   • Domain: {stats['learning_domain'].replace('_', ' ').title()}")
        print(f"   • Total Hours Used: {stats['total_hours_used']} / {stats['total_hours_available']}")
        print(f"   • Utilization: {stats['utilization_percentage']:.1f}%")
        print(f"   • Nodes Completed: {stats['nodes_completed']} / {stats['total_nodes']}")
        print(f"   • Expected Completion: {stats['expected_completion']} weeks")
        
        print(f"\n🛣️  LEARNING PATH ({len(path)} nodes):")
        for i, node in enumerate(path, 1):
            print(f"   {i:2d}. {node.title} ({node.estimated_time} hrs) - "
                  f"Difficulty: {node.difficulty}/10 - Load: {node.load}")

    def visualize_weekly_schedule(self, schedule: Dict[str, List[LearningNode]]):
        """Display weekly schedule with bar chart visualization"""
        print(f"\n📅 WEEKLY STUDY SCHEDULE:")
        print("-" * 60)
        
        for week, nodes in schedule.items():
            week_hours = sum(node.estimated_time for node in nodes)
            print(f"\n{week} ({week_hours} hours):")
            for node in nodes:
                print(f"   • {node.title} ({node.estimated_time} hrs)")

        # Create bar chart visualization
        self._plot_weekly_schedule(schedule)

    def _plot_weekly_schedule(self, schedule: Dict[str, List[LearningNode]]):
        """Plot weekly study hours distribution"""
        if not schedule:
            print("No schedule to plot")
            return
            
        plt.figure(figsize=(12, 6))
        weeks = list(schedule.keys())
        hours = [sum(n.estimated_time for n in schedule[w]) for w in weeks]
        
        bars = plt.bar(weeks, hours, color='skyblue', alpha=0.7)
        
        for bar, hour in zip(bars, hours):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{hour}h', ha='center', va='bottom', fontweight='bold')
        
        plt.title("⏳ Weekly Study Hours Distribution", fontsize=14, pad=20)
        plt.xlabel("Weeks")
        plt.ylabel("Total Study Hours")
        plt.xticks(rotation=45)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.show()

# ---------------- USER INPUT FUNCTIONS ----------------

def get_user_domain() -> LearningDomain:
    """Get user's preferred learning domain"""
    print("\n🎯 SELECT LEARNING DOMAIN:")
    print("1. AI & Machine Learning")
    print("2. Web Development")
    print("3. Cybersecurity")
    print("4. Cloud Computing")
    print("5. Full Stack (All domains)")
    
    while True:
        try:
            domain_choice = int(input("\nEnter your choice (1-5): ").strip())
            if domain_choice in [1, 2, 3, 4, 5]:
                break
            else:
                print("❌ Please enter a number between 1 and 5")
        except ValueError:
            print("❌ Please enter a valid number")
    
    domain_map = {
        1: LearningDomain.AI_ML,
        2: LearningDomain.WEB_DEV,
        3: LearningDomain.CYBERSECURITY,
        4: LearningDomain.CLOUD_COMPUTING,
        5: LearningDomain.FULL_STACK
    }
    return domain_map[domain_choice]

def get_user_input():
    """Get user input for learning preferences"""
    print("🎓 AI & DATA SCIENCE LEARNING PATH GENERATOR")
    print("="*50)
    
    # Get learning domain first
    learning_domain = get_user_domain()
    
    # Get learner level
    print("\n📚 SELECT YOUR CURRENT LEVEL:")
    print("1. Beginner (0-1 years experience)")
    print("2. Intermediate (1-3 years experience)") 
    print("3. Advanced (3+ years experience)")
    print("4. Researcher (Advanced + research focus)")
    
    while True:
        try:
            level_choice = int(input("\nEnter your choice (1-4): ").strip())
            if level_choice in [1, 2, 3, 4]:
                break
            else:
                print("❌ Please enter a number between 1 and 4")
        except ValueError:
            print("❌ Please enter a valid number")
    
    level_map = {
        1: LearnerType.BEGINNER,
        2: LearnerType.INTERMEDIATE, 
        3: LearnerType.ADVANCED,
        4: LearnerType.RESEARCHER
    }
    learner_type = level_map[level_choice]
    
    # Get time availability
    print("\n⏰ SELECT YOUR TIME AVAILABILITY:")
    print("1. Part-time (8 hrs/week - weekends or evenings)")
    print("2. Full-time (20 hrs/week - dedicated study)")
    print("3. Intensive (40 hrs/week - immersive learning)")
    
    while True:
        try:
            time_choice = int(input("\nEnter your choice (1-3): ").strip())
            if time_choice in [1, 2, 3]:
                break
            else:
                print("❌ Please enter a number between 1 and 3")
        except ValueError:
            print("❌ Please enter a valid number")
    
    time_map = {
        1: TimeAvailability.PART_TIME,
        2: TimeAvailability.FULL_TIME,
        3: TimeAvailability.INTENSIVE
    }
    time_availability = time_map[time_choice]
    
    # Get study duration
    print("\n📅 SELECT STUDY DURATION:")
    print("Recommended: 12-24 weeks for comprehensive learning")
    
    while True:
        try:
            weeks = int(input("\nEnter number of weeks (e.g., 12, 24, 36): ").strip())
            if weeks > 0 and weeks <= 104:  # Max 2 years
                break
            else:
                print("❌ Please enter a reasonable number of weeks (1-104)")
        except ValueError:
            print("❌ Please enter a valid number")
    
    return learner_type, time_availability, learning_domain, weeks

def load_dataset_from_json() -> List[Dict]:
    """Load dataset from JSON file using the configured path"""
    try:
        print(f"📁 Loading curriculum from: {JSON_FILE_PATH}")
        
        if not JSON_FILE_PATH.exists():
            print(f"❌ Error: JSON file not found at {JSON_FILE_PATH}")
            print("💡 Please check the JSON_FILE_PATH configuration")
            return []
        
        with open(JSON_FILE_PATH, "r", encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ Successfully loaded {len(data)} learning nodes")
            return data
            
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return []

def display_learning_domains(dataset: List[Dict]):
    """Display available learning domains from the curriculum"""
    print("\n🌐 AVAILABLE LEARNING DOMAINS IN CURRICULUM:")
    print("-" * 50)
    
    main_nodes = [node for node in dataset if node.get('type') == 'main_node']
    
    for i, node in enumerate(main_nodes, 1):
        print(f"{i}. {node['title']} - {node['estimated_time']} hrs")
        if 'subtopics' in node and node['subtopics']:
            print(f"   Topics: {', '.join(node['subtopics'][:3])}...")
        print()

def main():
    """Main function to run the learning path generator"""
    try:
        # Load the dataset
        dataset = load_dataset_from_json()
        if not dataset:
            print("❌ Cannot generate roadmap without curriculum data.")
            return
        
        print(f"\n📊 Curriculum loaded: {len(dataset)} total learning units")
        display_learning_domains(dataset)
        
        # Get user input
        learner_type, time_availability, learning_domain, study_weeks = get_user_input()
        
        # Generate learning path
        print(f"\n🚀 Generating your personalized learning path...")
        print(f"   • Domain: {learning_domain.value.replace('_', ' ').title()}")
        print(f"   • Level: {learner_type.value}")
        print(f"   • Time: {time_availability.value} ({study_weeks} weeks)")
        
        generator = LearningPathGenerator(dataset)
        
        path, weekly_schedule, stats = generator.get_recommended_path(
            learner_type=learner_type,
            time_availability=time_availability,
            learning_domain=learning_domain,
            study_weeks=study_weeks
        )
        
        # Display results
        if path:
            generator.visualize_path(path, stats)
            generator.visualize_weekly_schedule(weekly_schedule)
            
            print(f"\n🎉 Your personalized learning path is ready!")
            print(f"💡 You'll complete {stats['nodes_completed']} learning units in {stats['expected_completion']} weeks")
            
        else:
            print("\n❌ No suitable learning path found with your constraints.")
            print("💡 Try increasing your time availability or study duration.")
            
    except KeyboardInterrupt:
        print(f"\n\n👋 Program interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("💡 Please check your configuration and try again.")

# ---------------- RUN THE APPLICATION ----------------
if __name__ == "__main__":
    main()
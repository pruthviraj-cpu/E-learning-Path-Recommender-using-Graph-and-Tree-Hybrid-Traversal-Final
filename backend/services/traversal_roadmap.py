import json
import networkx as nx
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Set, Optional, Any
from enum import Enum


class LearnerType(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate" 
    ADVANCED = "advanced"
    RESEARCHER = "researcher"

class TimeAvailability(Enum):
    PART_TIME = "part_time"    # 5-10 hrs/week
    FULL_TIME = "full_time"    # 20-30 hrs/week  
    INTENSIVE = "intensive"    # 40+ hrs/week

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

# ---------------- MAIN CLASS ----------------
class LearningPathGenerator:
    def __init__(self, dataset: List[Dict]):
        self.nodes = self._create_nodes(dataset)
        self.graph = self._build_graph()
        self.main_nodes = [node for node in self.nodes.values() if node.type == "main_node"]
    
    def _create_nodes(self, dataset: List[Dict]) -> Dict[str, LearningNode]:
        """Create LearningNode objects from dataset with proper error handling"""
        nodes = {}
        for item in dataset:
            try:
                # Ensure all required fields are present with defaults
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
            
            # Add prerequisite edges
            for prereq in node.prerequisites:
                if prereq in self.nodes:
                    G.add_edge(prereq, node_id)
            
            # Add subnode relationships (for main nodes)
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
                           study_weeks: int = 12) -> Tuple[List[LearningNode], Dict, Dict]:
        """Generate a personalized learning path based on user profile"""
        
        # Calculate available time in hours
        total_available_hours = self.calculate_total_available_hours(time_availability, study_weeks)
        
        print(f"Available time: {total_available_hours} hours over {study_weeks} weeks")
        
        # Filter nodes based on learner type
        filtered_nodes = self._filter_nodes_by_learner_type(learner_type)
        
        # Get topological order considering prerequisites
        try:
            topological_order = list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            topological_order = list(self.graph.nodes())
        
        # Build path respecting prerequisites and time constraints
        path = []
        completed = set()
        total_time_used = 0
        
        for node_id in topological_order:
            if node_id not in filtered_nodes:
                continue
                
            node = self.nodes[node_id]
            
            # Check if prerequisites are satisfied
            prereqs_satisfied = all(prereq in completed for prereq in node.prerequisites)
            
            if prereqs_satisfied and node_id not in completed:
                # Check if adding this node exceeds time budget
                if total_time_used + node.estimated_time <= total_available_hours:
                    path.append(node)
                    completed.add(node_id)
                    total_time_used += node.estimated_time
                else:
                    # Skip if we can't fit it
                    continue
        
        # Create weekly schedule
        weekly_schedule = self._create_weekly_schedule(path, time_availability, study_weeks)
        
        stats = {
            'total_hours_used': total_time_used,
            'total_hours_available': total_available_hours,
            'utilization_percentage': (total_time_used / total_available_hours) * 100,
            'nodes_completed': len(completed),
            'total_nodes': len(filtered_nodes),
            'weeks': study_weeks,
            'hours_per_week': self.calculate_total_available_hours(time_availability, 1),
            'expected_completion': min(study_weeks, round(total_time_used / self.calculate_total_available_hours(time_availability, 1), 1))
        }
        
        return path, weekly_schedule, stats
    
    def _filter_nodes_by_learner_type(self, learner_type: LearnerType) -> Set[str]:
        """Filter nodes based on learner expertise level"""
        difficulty_thresholds = {
            LearnerType.BEGINNER: 4,      # Max difficulty 4
            LearnerType.INTERMEDIATE: 6,  # Max difficulty 6  
            LearnerType.ADVANCED: 8,      # Max difficulty 8
            LearnerType.RESEARCHER: 10    # All nodes
        }
        
        threshold = difficulty_thresholds[learner_type]
        return {node_id for node_id, node in self.nodes.items() 
                if node.difficulty <= threshold}
    
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
            # If adding this node exceeds weekly capacity, move to next week
            if current_week_hours + node.estimated_time > weekly_hours[time_availability]:
                if current_week_nodes:  # Only add week if it has content
                    schedule[f"Week {current_week}"] = current_week_nodes.copy()
                    current_week += 1
                    current_week_hours = 0
                    current_week_nodes = []
                
                # If we've exceeded total weeks, stop
                if current_week > total_weeks:
                    break
            
            current_week_nodes.append(node)
            current_week_hours += node.estimated_time
        
        # Add the final week
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
        
        # Add value labels on bars
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

    def visualize_graph(self, path: List[LearningNode], weekly_schedule: Dict[str, List[LearningNode]]):
        """Visualize the personalized learning roadmap as a clean, hierarchical graph."""
        if not path:
            print("No path to visualize")
            return
            
        node_ids = [n.id for n in path]
        G = self.graph.subgraph(node_ids)

        # Map node -> week number
        week_map = {}
        for week_label, nodes_in_week in weekly_schedule.items():
            week_num = int(week_label.split()[-1])
            for node in nodes_in_week:
                week_map[node.id] = week_num

        # Create a figure + axes explicitly
        fig, ax = plt.subplots(figsize=(16, 10))

        # Try hierarchical layout (requires Graphviz)
        try:
            pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
        except Exception:
            pos = nx.spring_layout(G, seed=42, k=3, iterations=50)

        # Color and size properties
        weeks = [week_map.get(n, 1) for n in G.nodes()]
        times = [G.nodes[n]["estimated_time"] for n in G.nodes()]
        node_sizes = [max(800, min(2000, t * 40)) for t in times]

        # Draw nodes
        nodes = nx.draw_networkx_nodes(
            G, pos,
            node_size=node_sizes,
            node_color=weeks,
            cmap=plt.cm.plasma,
            alpha=0.92,
            linewidths=2.0,
            edgecolors='black',
            ax=ax
        )

        # Draw edges
        nx.draw_networkx_edges(
            G, pos,
            arrowstyle='-|>',
            arrowsize=20,
            width=2.5,
            edge_color='gray',
            alpha=0.7,
            connectionstyle="arc3,rad=0.1",
            ax=ax
        )

        # Smart labels: multiline with week info
        labels = {}
        for n in G.nodes():
            title = G.nodes[n]["title"]
            hours = G.nodes[n]["estimated_time"]
            week = week_map.get(n, None)
            difficulty = G.nodes[n]["difficulty"]
            labels[n] = f"{title}\n({hours}h | W{week} | D{difficulty})" if week else f"{title}\n({hours}h)"

        nx.draw_networkx_labels(
            G, pos,
            labels=labels,
            font_size=8,
            font_weight='bold',
            verticalalignment='center',
            horizontalalignment='center',
            ax=ax
        )

        # Title & Colorbar
        ax.set_title("📚 Personalized Learning Roadmap Graph (Color = Week, Size = Hours)", 
                    fontsize=16, pad=25)
        sm = plt.cm.ScalarMappable(cmap=plt.cm.plasma, 
                                 norm=plt.Normalize(vmin=min(weeks), vmax=max(weeks)))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label("Week Progression", fontsize=12)

        ax.axis("off")
        plt.tight_layout()
        plt.show()

# ---------------- LOAD DATASET & CREATE ROADMAP ----------------
def load_dataset_from_json(file_path: str) -> List[Dict]:
    """Load dataset from JSON file"""
    with open(file_path, "r") as f:
        return json.load(f)

def create_roadmap(file_path: str, learner_type: LearnerType, 
                   time_availability: TimeAvailability, study_weeks: int = 12):
    """Main function to create and display learning roadmap"""
    dataset = load_dataset_from_json(file_path)
    generator = LearningPathGenerator(dataset)
    
    path, weekly_schedule, stats = generator.get_recommended_path(
        learner_type=learner_type,
        time_availability=time_availability,
        study_weeks=study_weeks
    )
    
    # Display all visualizations
    generator.visualize_path(path, stats)
    generator.visualize_weekly_schedule(weekly_schedule)
    if path:  # Only visualize graph if there's a path
        generator.visualize_graph(path, weekly_schedule)
    
    return path, weekly_schedule, stats

# ---------------- EXAMPLE USAGE ----------------
if __name__ == "__main__":
    # Example 1: Beginner with part-time availability
    print("🚀 GENERATING LEARNING ROADMAPS")
    print("="*50)
    
    print("\n👶 BEGINNER LEARNER (Part-time, 12 weeks):")
    create_roadmap("Learning_Path.json", LearnerType.BEGINNER, TimeAvailability.PART_TIME, 12)
    
    print("\n\n🎯 INTERMEDIATE LEARNER (Full-time, 12 weeks):")
    create_roadmap("Learning_Path.json", LearnerType.INTERMEDIATE, TimeAvailability.FULL_TIME, 12)
    
    print("\n\n🔥 ADVANCED LEARNER (Intensive, 16 weeks):")
    create_roadmap("Learning_Path.json", LearnerType.ADVANCED, TimeAvailability.INTENSIVE, 16)
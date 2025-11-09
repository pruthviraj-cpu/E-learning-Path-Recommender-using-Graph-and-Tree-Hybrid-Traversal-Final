import json
import networkx as nx
import numpy as np
from typing import List, Dict, Tuple, Set, Optional, Any
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import random

# ---------- ADDED FOR GAN FORECASTER ----------

def compute_difficulty(quiz_score=None, estimated_time=None, prereq_count=None):
    """Estimate topic difficulty dynamically if not provided."""
    base_difficulty = 5.0

    if quiz_score is not None:
        base_difficulty += (1 - quiz_score) * 3  # harder if score is low
    if estimated_time is not None:
        base_difficulty += (estimated_time / 20)  # 20h ≈ +1 difficulty
    if prereq_count is not None:
        base_difficulty += prereq_count * 0.5

    # clamp to [1, 10]
    return min(max(base_difficulty, 1.0), 10.0)


def compute_load(difficulty, estimated_time, quiz_score=None):
    """Estimate learner load ('low', 'medium', 'high') dynamically."""
    if quiz_score is None:
        quiz_score = 0.7  # fallback

    # Compute a numeric load index
    load_index = difficulty * (estimated_time / 10) * (1 - quiz_score)
    
    if load_index < 10:
        return "low"
    elif load_index < 25:
        return "medium"
    else:
        return "high"

# ---------- END ADDED FOR GAN FORECASTER ----------

# ========== CONFIGURATION ==========
JSON_FILE_PATH = Path(__file__).parent.parent / "database" / "learning_path.json"

class LearnerType(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate" 
    ADVANCED = "advanced"
    RESEARCHER = "researcher"

class TimeAvailability(Enum):
    PART_TIME = "part_time"    # 8 hrs/week
    FULL_TIME = "full_time"    # 20 hrs/week  
    INTENSIVE = "intensive"    # 40 hrs/week

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
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'estimated_time': self.estimated_time,
            'load': self.load,
            'difficulty': self.difficulty,
            'prerequisites': self.prerequisites,
            'subnodes': self.subnodes,
            'subtopics': self.subtopics,
            'resources': self.resources,
            'embedding': self.embedding
        }

class LearningPathService:
    def __init__(self):
        self.dataset = self._load_dataset()
        self.nodes = self._create_nodes(self.dataset)
        self.graph = self._build_graph()
        self.domain_mapping = self._create_domain_mapping()
        print(f"Service initialized with {len(self.nodes)} nodes")
    
    def _load_dataset(self) -> List[Dict]:
        """Load dataset from JSON file"""
        try:
            print(f"📁 Loading dataset from: {JSON_FILE_PATH}")
            if not JSON_FILE_PATH.exists():
                raise FileNotFoundError(f"JSON file not found at {JSON_FILE_PATH}")
            
            with open(JSON_FILE_PATH, "r", encoding='utf-8') as f:
                data = json.load(f)
                print(f"Loaded {len(data)} nodes from JSON")
                return data
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return []
    
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
            LearningDomain.FULL_STACK: []  # All nodes
        }
    
    def _create_nodes(self, dataset: List[Dict]) -> Dict[str, LearningNode]:
        """Create LearningNode objects from dataset"""
        nodes = {}
        for item in dataset:
            try:
                # nodes[item['id']] = LearningNode(
                #     id=item['id'],
                #     title=item['title'],
                #     type=item['type'],
                #     estimated_time=item['estimated_time'],
                #     load=item['load'],
                #     difficulty=item['difficulty'],
                #     prerequisites=item.get('prerequisites', []),
                #     subnodes=item.get('subnodes', []),
                #     subtopics=item.get('subtopics', []),
                #     resources=item.get('resources', {}),
                #     embedding=item.get('embedding', [])
                # )

                # ---------- ADDED FOR GAN FORECASTER ----------
                # Auto-fill missing difficulty or load
                estimated_time = item.get('estimated_time', 10)
                quiz_score = item.get('quiz_score', 0.7)
                prereqs = item.get('prerequisites', [])
    
                difficulty = item.get('difficulty')
                if difficulty is None:
                    difficulty = compute_difficulty(quiz_score, estimated_time, len(prereqs))
    
                load = item.get('load')
                if load is None:
                    load = compute_load(difficulty, estimated_time, quiz_score)
    
                nodes[item['id']] = LearningNode(
                    id=item['id'],
                    title=item.get('title', item['id']),
                    type=item.get('type', 'module'),
                    estimated_time=estimated_time,
                    load=load,
                    difficulty=difficulty,
                    prerequisites=prereqs,
                    subnodes=item.get('subnodes', []),
                    subtopics=item.get('subtopics', []),
                    resources=item.get('resources', {}),
                    embedding=item.get('embedding', [])

                    # ---------- ADDED FOR GAN FORECASTER ----------
                )
            except Exception as e:
                print(f"Error creating node {item.get('id', 'unknown')}: {e}")
                continue
        
        print(f"Created {len(nodes)} LearningNode objects")
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
        
        print(f"Built graph with {len(G.nodes())} nodes and {len(G.edges())} edges")
        return G
    
    def calculate_total_available_hours(self, time_availability: TimeAvailability, weeks: int) -> int:
        """Calculate total available hours based on time availability and duration"""
        weekly_hours = {
            TimeAvailability.PART_TIME: 8,
            TimeAvailability.FULL_TIME: 20, 
            TimeAvailability.INTENSIVE: 40
        }
        return weekly_hours[time_availability] * weeks
    
# If we want to add the GAN Path Forecaster then it shpuld be added here.

    def generate_learning_path(self, 
                            learner_type: str,
                            time_availability: str,
                            learning_domain: str,
                            study_weeks: int = 12) -> Dict[str, Any]:
        """Generate a personalized learning path based on user profile"""
        
        print(f"\n🎯 Generating path for:")
        print(f"   • Domain: {learning_domain}")
        print(f"   • Level: {learner_type}")
        print(f"   • Time: {time_availability}")
        print(f"   • Weeks: {study_weeks}")
        
        # Convert string inputs to Enum
        try:
            learner_type_enum = LearnerType(learner_type)
            time_availability_enum = TimeAvailability(time_availability)
            learning_domain_enum = LearningDomain(learning_domain)
        except ValueError as e:
            raise ValueError(f"Invalid input parameter: {e}")
        
        total_available_hours = self.calculate_total_available_hours(time_availability_enum, study_weeks)
        print(f"⏰ Total available hours: {total_available_hours}")
        
        # Filter nodes by domain and learner type
        domain_filtered_nodes = self._filter_nodes_by_domain(learning_domain_enum)
        print(f"🔍 Domain filtered nodes: {len(domain_filtered_nodes)}")
        
        filtered_nodes = self._filter_nodes_by_learner_type(learner_type_enum, domain_filtered_nodes)
        print(f"🎓 Learner type filtered nodes: {len(filtered_nodes)}")
        
        # Debug: Show which nodes are being considered
        if filtered_nodes:
            print("📋 Nodes considered for path:")
            for node_id in filtered_nodes:
                node = self.nodes[node_id]
                print(f"   • {node.title} (Difficulty: {node.difficulty}, Time: {node.estimated_time}hrs)")
        else:
            print("No nodes available after filtering!")
            print(f"   Domain nodes: {domain_filtered_nodes}")
            print(f"   All nodes: {list(self.nodes.keys())[:10]}...")  # Show first 10 nodes
        
        try:
            topological_order = list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            topological_order = list(self.graph.nodes())
        
        path_nodes = []
        completed = set()
        total_time_used = 0
        
        for node_id in topological_order:
            if node_id not in filtered_nodes:
                continue
                
            node = self.nodes[node_id]
            
            prereqs_satisfied = all(prereq in completed for prereq in node.prerequisites)
            
            if prereqs_satisfied and node_id not in completed:
                if total_time_used + node.estimated_time <= total_available_hours:
                    path_nodes.append(node.to_dict())
                    completed.add(node_id)
                    total_time_used += node.estimated_time
                else:
                    print(f"⏳ Skipping {node.title} - exceeds available time")
        
        print(f"Generated path with {len(path_nodes)} nodes, total time: {total_time_used} hours")
        
        weekly_schedule = self._create_weekly_schedule(path_nodes, time_availability_enum, study_weeks)
        
        stats = {
            'total_hours_used': total_time_used,
            'total_hours_available': total_available_hours,
            'utilization_percentage': (total_time_used / total_available_hours) * 100 if total_available_hours > 0 else 0,
            'nodes_completed': len(completed),
            'total_nodes': len(filtered_nodes),
            'weeks': study_weeks,
            'hours_per_week': self.calculate_total_available_hours(time_availability_enum, 1),
            'expected_completion': min(study_weeks, round(total_time_used / self.calculate_total_available_hours(time_availability_enum, 1), 1)) if total_time_used > 0 else 0,
            'learning_domain': learning_domain
        }
        
        return {
            'path': path_nodes,
            'weekly_schedule': weekly_schedule,
            'stats': stats,
            'user_preferences': {
                'learner_type': learner_type,
                'time_availability': time_availability,
                'learning_domain': learning_domain,
                'study_weeks': study_weeks
            }
        }
    
    def _filter_nodes_by_domain(self, learning_domain: LearningDomain) -> Set[str]:
        """Filter nodes based on selected learning domain"""
        if learning_domain == LearningDomain.FULL_STACK:
            print("🌐 Using FULL_STACK - all nodes included")
            return set(self.nodes.keys())
        
        domain_main_nodes = self.domain_mapping[learning_domain]
        domain_nodes = set()
        
        print(f"🔍 Looking for domain main nodes: {domain_main_nodes}")
        
        for main_node_id in domain_main_nodes:
            if main_node_id in self.nodes:
                print(f"Found main node: {main_node_id}")
                domain_nodes.add(main_node_id)
                self._add_subnodes_recursively(main_node_id, domain_nodes)
            else:
                print(f"Main node not found: {main_node_id}")
        
        print(f"📊 Domain nodes found: {len(domain_nodes)}")
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
            LearnerType.BEGINNER: 4,
            LearnerType.INTERMEDIATE: 6,  
            LearnerType.ADVANCED: 8,
            LearnerType.RESEARCHER: 10
        }
        
        threshold = difficulty_thresholds[learner_type]
        filtered = {node_id for node_id in node_set 
                   if self.nodes[node_id].difficulty <= threshold}
        
        print(f"🎓 Learner type filter: {learner_type.value} (max difficulty: {threshold})")
        print(f"   Before filter: {len(node_set)} nodes")
        print(f"   After filter: {len(filtered)} nodes")
        
        return filtered
    
    def _create_weekly_schedule(self, path: List[Dict], 
                              time_availability: TimeAvailability, 
                              total_weeks: int) -> Dict[str, List[Dict]]:
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
            if current_week_hours + node['estimated_time'] > weekly_hours[time_availability]:
                if current_week_nodes:
                    schedule[f"Week {current_week}"] = current_week_nodes.copy()
                    current_week += 1
                    current_week_hours = 0
                    current_week_nodes = []
                
                if current_week > total_weeks:
                    break
            
            current_week_nodes.append(node)
            current_week_hours += node['estimated_time']
        
        if current_week_nodes and current_week <= total_weeks:
            schedule[f"Week {current_week}"] = current_week_nodes
        
        print(f"Created schedule with {len(schedule)} weeks")
        return schedule

# Global service instance
path_service = LearningPathService()


# ----------- ADDED FOR GAN FORECASTER ----------
# ----------- Learner Path Retrieval for Gan Forecaster ----------

def get_learner_path(learner_id: str):
    """
    Retrieve the learner's generated learning path.
    This mock version assumes a JSON or in-memory dataset already exists.
    Replace this with your real learner-path retrieval logic.
    """
    # For now, just load from the dataset and simulate learner path
    learner_path = []
    for node_id, node in path_service.nodes.items():
        learner_path.append({
            "id": node.id,
            "title": node.title,
            "difficulty": node.difficulty,
            "embedding": node.embedding if node.embedding else [],
            "quiz_score": np.random.uniform(0.5, 0.9),  # mock quiz scores
            "timestamp": datetime.now().isoformat()
        })
    
    # Optionally, filter only part of the path for realism
    learner_path = learner_path[:min(20, len(learner_path))]

    print(f"Retrieved learning path for {learner_id} with {len(learner_path)} nodes.")
    return learner_path

# -----------GAN Forecaster Service Ends -----------
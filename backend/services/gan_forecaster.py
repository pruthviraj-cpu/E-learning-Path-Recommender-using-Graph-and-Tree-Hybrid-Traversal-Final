import importlib
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import networkx as nx
from typing import List, Dict, Any, Optional, Callable, Tuple
from sqlalchemy.orm import Session
from services import path_service
from services.path_service import LearningPathService
from models.database import get_db
from models.user_path_models import UserLearningPath
from models.quiz_results import QuizResult
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ----------------------------
# Real Data Path Fetcher
# ----------------------------

def _get_real_learner_path(learner_id: str) -> List[Dict[str, Any]]:
    """
    Fetch real learner path from database with quiz scores and progress data
    """
    try:
        logger.info(f"📥 Fetching real learner data for user: {learner_id}")
        db = next(get_db())
        user_id = int(learner_id)
        
        # Get user's active learning path
        user_path = db.query(UserLearningPath).filter(
            UserLearningPath.user_id == user_id,
            UserLearningPath.is_active == 1
        ).first()
        
        if not user_path or not user_path.path_data:
            logger.warning(f"❌ No active learning path found for user {user_id}")
            print(f"No path data found for user {user_id}")
            return []
        
        logger.info(f"📁 User path found: '{user_path.title}' (Domain: {user_path.learning_domain})")
        
        print(f"Path data type: {type(user_path.path_data)}")
        # print(f"Path data: {user_path.path_data}")
        
        # Get user's quiz results
        quiz_results = db.query(QuizResult).filter(
            QuizResult.user_id == user_id
        ).all()

        logger.info(f"📊 Found {len(quiz_results)} quiz results for user {user_id}")
        
        # Create quiz score mapping by module/topic
        quiz_scores = {}
        for quiz in quiz_results:
            key = quiz.module_id or quiz.topic
            if key not in quiz_scores:
                quiz_scores[key] = []
            quiz_scores[key].append(quiz.score / 100.0)  # Convert to 0-1 scale
        
        avg_quiz_scores = {
            key: sum(scores) / len(scores) 
            for key, scores in quiz_scores.items()
        }

        logger.info(f"📈 Quiz scores calculated for {len(avg_quiz_scores)} modules")
        
        # Build path nodes with real data
        path_nodes = []
        
        # Handle different possible path data structures
        path_data = user_path.path_data
        
        # Case 1: path_data is a dict with 'path' key
        if isinstance(path_data, dict) and 'path' in path_data:
            actual_path = path_data['path']
            logger.info(f"📋 Path structure: dict with {len(actual_path)} nodes")
        # Case 2: path_data is directly the list
        elif isinstance(path_data, list):
            actual_path = path_data
            logger.info(f"📋 Path structure: list with {len(actual_path)} nodes")
        else:
            logger.warning(f"❓ Unknown path data structure: {type(path_data)}")
            actual_path = []
        
        completed_nodes = user_path.completed_nodes or []
        
        print(f"Processing {len(actual_path)} path nodes")
        
        for node in actual_path:
            # Handle both dict and object-like nodes
            if isinstance(node, dict):
                node_id = node.get('id', '')
                node_title = node.get('title', '')
                difficulty = node.get('difficulty', 5.0)
                estimated_time = node.get('estimated_time', 10.0)
                prerequisites = node.get('prerequisites', [])
            else:
                # If it's not a dict, try to access attributes
                node_id = getattr(node, 'id', '')
                node_title = getattr(node, 'title', '')
                difficulty = getattr(node, 'difficulty', 5.0)
                estimated_time = getattr(node, 'estimated_time', 10.0)
                prerequisites = getattr(node, 'prerequisites', [])
            
            # Check if node is completed
            is_completed = False
            for completed in completed_nodes:
                if isinstance(completed, dict):
                    if completed.get('id') == node_id or completed.get('title') == node_title:
                        is_completed = True
                        break
                else:
                    if completed == node_id or completed == node_title:
                        is_completed = True
                        break
            
            # Get quiz score for this module
            quiz_score = avg_quiz_scores.get(node_id) or avg_quiz_scores.get(node_title, 0.7)
            
            # Create embedding vector
            embedding = [
                difficulty / 10.0,  # Normalize difficulty to 0-1
                quiz_score,         # Actual quiz performance
                estimated_time / 40.0,  # Normalize time
                float(is_completed) # Completion status
            ]
            
            path_node = {
                "id": node_id,
                "title": node_title,
                "difficulty": difficulty,
                "estimated_time": estimated_time,
                "quiz_score": quiz_score,
                "completed": is_completed,
                "embedding": embedding,
                "prerequisites": prerequisites
            }
            
            path_nodes.append(path_node)
        
        print(f"Retrieved real learning path for user {user_id} with {len(path_nodes)} nodes")
        logger.info(f"🎯 Built learning path with {len(path_nodes)} processed nodes")
        
        return path_nodes
        
    except Exception as e:
        print(f"Error fetching real learner path: {e}")
        import traceback
        # print(f"Traceback: {traceback.format_exc()}")
        return []

# Use real data fetcher
_get_learner_path = _get_real_learner_path

# ----------------------------
# GAN Components
# ----------------------------
class Generator(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 64, output_dim: Optional[int] = None):
        super(Generator, self).__init__()
        if output_dim is None:
            output_dim = input_dim
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, z):
        return self.net(z)


class Discriminator(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 64):
        super(Discriminator, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)

# ----------------------------
# Helper Utilities
# ----------------------------
def _safe_float(v, fallback=0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(fallback)

def _pad_or_truncate(vec: List[float], target_dim: int) -> np.ndarray:
    arr = np.array(vec, dtype=float)
    if arr.size == target_dim:
        return arr
    if arr.size > target_dim:
        return arr[:target_dim]
    pad = np.zeros(target_dim - arr.size, dtype=float)
    return np.concatenate([arr, pad])

def _detect_embedding_dim(path: List[Dict[str, Any]], preferred: int = 16) -> int:
    for node in path:
        emb = node.get("embedding")
        if emb and isinstance(emb, (list, tuple, np.ndarray)) and len(emb) > 0:
            return len(emb)
    return preferred

# ----------------------------
# GAN Forecaster
# ----------------------------
class GANForecaster:
    MIN_DIFFICULTY_SPIKE = 1.0
    MIN_SUCCESS_DIFF = 0.05 
    

    def __init__(self,
                 embedding_dim: Optional[int] = None,
                 device: str = "cpu",
                 gen_hidden: int = 64,
                 dis_hidden: int = 64,
                 train_epochs: int = 200,
                 path_service: Optional[LearningPathService] = None):
        self.device = torch.device(device)
        self._static_embedding_dim = embedding_dim
        self.gen_hidden = gen_hidden
        self.dis_hidden = dis_hidden
        self.train_epochs = train_epochs
        self.path_service = path_service
        self.generator = None
        self.discriminator = None
        self.optim_G = None
        self.optim_D = None
        self.loss_fn = nn.BCELoss()

        # Core modules will be dynamically detected
        self._core_modules = None
        logger.info("🎯 GAN Forecaster initialized")
        if path_service:
            logger.info(f"📚 Path service connected with {len(path_service.nodes)} nodes")
        else:
            logger.warning("⚠️ No path service provided - core module detection may be limited")
    # ----------------------------
    # GAN model setup
    # ----------------------------

    def _detect_core_modules(self) -> List[str]:
        """
        Dynamically detect core modules from the learning path JSON data
        Core modules are defined as:
        1. Main nodes with no prerequisites (foundational)
        2. Main nodes that are prerequisites for many other nodes
        3. Nodes with type 'main_node' that appear early in topological order
        """
        if self._core_modules is not None:
            return self._core_modules
            
        if not self.path_service or not self.path_service.nodes:
            # Fallback to some essential modules if service not available
            return ["python_basics", "foundational_skills", "web_dev_foundations", "cyber_foundations"]
        
        core_modules = set()
        nodes = self.path_service.nodes
        graph = self.path_service.graph
        
        # Strategy 1: Main nodes with no prerequisites (foundational)
        for node_id, node in nodes.items():
            if (node.type == "main_node" and 
                (not node.prerequisites or len(node.prerequisites) == 0)):
                core_modules.add(node.title)
                print(f"🔍 Found core module (no prereqs): {node.title}")
        
        # Strategy 2: Nodes that are prerequisites for many other nodes
        prerequisite_counts = {}
        for node_id, node in nodes.items():
            for prereq in node.prerequisites:
                if prereq in nodes:
                    prereq_title = nodes[prereq].title
                    prerequisite_counts[prereq_title] = prerequisite_counts.get(prereq_title, 0) + 1
        
        # Add top prerequisite nodes as core modules
        top_prereqs = sorted(prerequisite_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for module_title, count in top_prereqs:
            if count >= 2:  # Only include if it's a prerequisite for at least 2 modules
                core_modules.add(module_title)
                print(f"🔍 Found core module (prereq for {count} modules): {module_title}")
        
        # Strategy 3: Early nodes in topological order (if graph is acyclic)
        try:
            topological_order = list(nx.topological_sort(graph))
            # Take first few main nodes from topological order
            early_main_nodes = []
            for node_id in topological_order[:10]:  # Check first 10 nodes
                node = nodes.get(node_id)
                if node and node.type == "main_node":
                    early_main_nodes.append(node.title)
            
            # Add the first 3 early main nodes as core
            for title in early_main_nodes[:3]:
                core_modules.add(title)
                print(f"🔍 Found core module (early in topology): {title}")
                
        except nx.NetworkXUnfeasible:
            # Graph has cycles, use alternative strategy
            print("⚠️ Graph has cycles, using alternative core module detection")
            
        # Strategy 4: Look for explicitly marked foundational nodes
        foundational_keywords = ['foundation', 'fundamental', 'basic', 'core', 'essential']
        for node_id, node in nodes.items():
            if any(keyword in node.title.lower() for keyword in foundational_keywords):
                core_modules.add(node.title)
                print(f"🔍 Found core module (foundational keyword): {node.title}")
        
        self._core_modules = list(core_modules)
        print(f"🎯 Detected {len(self._core_modules)} core modules: {self._core_modules}")
        return self._core_modules
    
    @property
    def CORE_MODULES(self) -> List[str]:
        """Property to access dynamically detected core modules"""
        return self._detect_core_modules()
    

    def _build_models_for_dim(self, dim: int):
        self.generator = Generator(dim, self.gen_hidden, dim).to(self.device)
        self.discriminator = Discriminator(dim, self.dis_hidden).to(self.device)
        self.optim_G = optim.Adam(self.generator.parameters(), lr=1e-3)
        self.optim_D = optim.Adam(self.discriminator.parameters(), lr=1e-3)

    def _prepare_embeddings_matrix(self, path: List[Dict[str, Any]]) -> Tuple[np.ndarray, int]:
        dim = self._static_embedding_dim or _detect_embedding_dim(path, preferred=16)
        rows = []
        for node in path:
            emb_raw = node.get("embedding", [])
            if not isinstance(emb_raw, (list, tuple, np.ndarray)) or len(emb_raw) == 0:
                difficulty = _safe_float(node.get("difficulty", 5.0))
                quiz = _safe_float(node.get("quiz_score", 0.7))
                est_time = _safe_float(node.get("estimated_time", 10.0))
                emb_raw = [difficulty / 10.0, quiz, est_time / 40.0]
            rows.append(_pad_or_truncate(emb_raw, dim))
        return np.vstack(rows).astype(float), dim

    def train_gan(self, base_embeddings: np.ndarray, epochs: Optional[int] = None):
        if base_embeddings.size == 0:
            logger.warning("⚠️ No embeddings to train GAN")
            return
        epochs = epochs or self.train_epochs
        batch_n, dim = base_embeddings.shape
        self._build_models_for_dim(dim)

        real = torch.tensor(base_embeddings, dtype=torch.float32).to(self.device)
        for epoch in range(epochs):
            noise = torch.randn(batch_n, dim, device=self.device)
            with torch.no_grad():
                fake = self.generator(noise).detach()

            real_labels = torch.ones(batch_n, 1, device=self.device)
            fake_labels = torch.zeros(batch_n, 1, device=self.device)

            real_pred = self.discriminator(real)
            fake_pred = self.discriminator(fake)
            loss_D = self.loss_fn(real_pred, real_labels) + self.loss_fn(fake_pred, fake_labels)
            self.optim_D.zero_grad()
            loss_D.backward()
            self.optim_D.step()

            noise = torch.randn(batch_n, dim, device=self.device)
            generated = self.generator(noise)
            fake_pred_for_g = self.discriminator(generated)
            loss_G = self.loss_fn(fake_pred_for_g, real_labels)
            self.optim_G.zero_grad()
            loss_G.backward()
            if epoch % 20 == 0 or epoch == epochs - 1:
                logger.info(f"   Epoch {epoch+1}/{epochs} - D_loss: {loss_D.item():.4f}, G_loss: {loss_G.item():.4f}")
            self.optim_G.step()
        logger.info("✅ GAN training completed")


    # ----------------------------
    # Core evaluation
    # ----------------------------
    def evaluate_path(self, learner_id: str) -> Dict[str, Any]:
        path = _get_learner_path(learner_id)
        logger.info(f"🔍 Starting GAN evaluation for learner: {learner_id}")
        if not path:
            raise ValueError(f"No learner path found for ID: {learner_id}")

        logger.info(f"📊 Retrieved path with {len(path)} nodes for user {learner_id}")
        
        # Log first 3 nodes as sample
        sample_nodes = path[:3]
        for i, node in enumerate(sample_nodes):
            logger.info(f"   Node {i+1}: {node.get('title')} (Diff: {node.get('difficulty')}, Completed: {node.get('completed')})")

        base_embs, dim = self._prepare_embeddings_matrix(path)
        logger.info(f"🧮 Created embeddings matrix: {base_embs.shape} (nodes: {base_embs.shape[0]}, features: {base_embs.shape[1]})")
        
        logger.info("🤖 Training GAN...")
        self.train_gan(base_embs)

        with torch.no_grad():
            noise = torch.randn(base_embs.shape[0], dim, device=self.device)
            fake_embs = self.generator(noise).cpu().numpy()

        metrics = self._compute_metrics(path, base_embs, fake_embs)
        metrics["revision_advice"] = self._detect_revision_points(path, metrics)
        logger.info(f"✅ GAN Evaluation Complete - Success Probability: {metrics['success_probability']:.2%}")
        return metrics

    def _compute_metrics(self, real_path, real_embs, synthetic_embs) -> Dict[str, Any]:
        current_emb = np.mean(real_embs, axis=0)
        future_emb = np.mean(synthetic_embs, axis=0)
        dist = float(np.linalg.norm(future_emb - current_emb))
        success_prob = 1.0 / (1.0 + dist)

        difficulties = [float(n.get("difficulty", 5.0)) for n in real_path]
        diff_changes = np.diff(difficulties)
        spike_index = int(np.argmax(diff_changes)) if len(diff_changes) > 0 else -1
        spike_value = float(np.max(diff_changes)) if len(diff_changes) > 0 else 0.0
        spike_module = real_path[spike_index + 1].get("title") if spike_index >= 0 else None

        return {
            "success_probability": round(success_prob, 4),
            "difficulty_spike": round(spike_value, 3),
            "spike_module": spike_module,
            "n_nodes": len(real_path)
        }

    def _detect_revision_points(self, path, metrics):
        spike_mod = metrics.get("spike_module")
        if spike_mod:
            advice = {
                "revision_module": spike_mod,
                "message": f"Consider adding a short revision module before '{spike_mod}' to smooth the difficulty jump.",
                "location": "before_spike"
            }
        else:
            advice = {
                "revision_module": None,
                "message": "No major difficulty spikes detected — continue learning path as is.",
                "location": "none"
            }
        return advice

    # ----------------------------
    # Dependency & core check
    # ----------------------------
    def _has_dependents(self, module_id: str, path: List[Dict[str, Any]]) -> bool:
        for node in path:
            prereqs = node.get("prerequisites", [])
            if module_id in prereqs:
                return True
        return False

    def should_skip_module(self, learner_id: str, module_title_or_id: str) -> Dict[str, Any]:
        logger.info(f"🔍 Analyzing skip possibility for module: '{module_title_or_id}' (User: {learner_id})")
        path = _get_learner_path(learner_id)

        if not path:
            raise ValueError(f"No learner path for {learner_id}")

         # 1. Never skip core modules (now dynamically detected)
        core_modules = self._detect_core_modules()
        if module_title_or_id in core_modules:
            logger.info(f"🚫 Module '{module_title_or_id}' is CORE - cannot skip")
            return {
                "module": module_title_or_id,
                "advice": f"This is a foundational core module ('{module_title_or_id}') and should not be skipped.",
                "skip_recommended": False,
                "reason": "core_module"
            }

        # 2. Check dependency graph
        if self._has_dependents(module_title_or_id, path):
            logger.info(f"🔗 Module '{module_title_or_id}' has dependents - cannot skip")
            return {
                "module": module_title_or_id,
                "advice": f"Cannot skip '{module_title_or_id}' because later modules depend on it.",
                "skip_recommended": False,
                "reason": "has_dependents"
            }
        logger.info(f"📈 Running GAN analysis for skip scenario...")
        # 3 Evaluate GAN impact
        base_metrics = self.evaluate_path(learner_id)
        modified_path = [n for n in path if n.get("title") != module_title_or_id and n.get("id") != module_title_or_id]
        if not modified_path:
            logger.warning(f"⚠️ Cannot skip - this is the only module left")
            return {
                "module": module_title_or_id,
                "advice": "Cannot skip — this is the only module left in the path.",
                "skip_recommended": False
            }

        mod_embs, dim = self._prepare_embeddings_matrix(modified_path)
        self.train_gan(mod_embs, epochs=max(20, self.train_epochs // 10))
        with torch.no_grad():
            noise = torch.randn(mod_embs.shape[0], dim, device=self.device)
            fake_mod = self.generator(noise).cpu().numpy()

        after_metrics = self._compute_metrics(modified_path, mod_embs, fake_mod)

        # 4Apply conservative thresholds
        base_success = base_metrics["success_probability"]
        after_success = after_metrics["success_probability"]
        logger.info(f"📊 Skip Analysis Results:")
        logger.info(f"   Before skip: {base_success:.2%} success probability")
        logger.info(f"   After skip:  {after_success:.2%} success probability")
        logger.info(f"   Difference:  {after_success - base_success:+.2%}")
        difficulty_spike = after_metrics["difficulty_spike"]

        skip_recommended = False
        advice = ""

        if (difficulty_spike < base_metrics["difficulty_spike"] - self.MIN_DIFFICULTY_SPIKE or
            after_success >= base_success - self.MIN_SUCCESS_DIFF):
            skip_recommended = True
            advice = f"Skipping '{module_title_or_id}' is likely safe."
        else:
            skip_recommended = False
            advice = f"Skipping '{module_title_or_id}' may increase difficulty or reduce learning success."

        return {
            "module": module_title_or_id,
            "before_metrics": base_metrics,
            "after_metrics": after_metrics,
            "advice": advice,
            "skip_recommended": skip_recommended
        }

    # In gan_forecaster.py - IMPROVE suggest_skips:

    def suggest_skips(self, learner_id: str) -> List[str]:
        try:
            logger.info(f"🔍 Finding skippable modules for user: {learner_id}")
            path = _get_learner_path(learner_id)
            if not path:
                logger.warning(f"❌ No path found for user {learner_id}")
                return []
                
            suggestions = []
            logger.info(f"📋 Analyzing {len(path)} modules for skip potential")
            
            for i, node in enumerate(path):
                module_id = node.get("title") or node.get("id")
                logger.info(f"   Checking module {i+1}/{len(path)}: {module_id}")
                
                try:
                    result = self.should_skip_module(learner_id, module_id)
                    if result.get("skip_recommended"):
                        suggestions.append(module_id)
                        logger.info(f"✅ Added to skip list: {module_id}")
                except Exception as e:
                    logger.error(f"❌ Error analyzing {module_id}: {e}")
                    continue
            
            logger.info(f"🎯 Found {len(suggestions)} skippable modules")
            return suggestions
            
        except Exception as e:
            logger.error(f"💥 Error in suggest_skips: {e}")
            return []
    
    def recommend_revision_based_on_quiz_performance(
        self, 
        user_id: str, 
        quiz_performance_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Recommend revision nodes based on quiz performance analysis
        """
        try:
            # Get current path evaluation
            path_metrics = self.evaluate_path(user_id)
            success_prob = path_metrics["success_probability"]
            
            # Analyze quiz performance
            weak_modules = []
            for quiz in quiz_performance_data:
                if quiz.get('score', 0) < 70:  # Below 70% is weak
                    weak_modules.append({
                        'module': quiz.get('module'),
                        'score': quiz.get('score'),
                        'timestamp': quiz.get('timestamp')
                    })
            
            # Remove duplicates and get unique weak modules
            unique_weak_modules = {}
            for module in weak_modules:
                mod_name = module['module']
                if mod_name not in unique_weak_modules or module['score'] < unique_weak_modules[mod_name]['score']:
                    unique_weak_modules[mod_name] = module
            
            weak_modules_list = list(unique_weak_modules.values())
            
            # Generate revision recommendations
            revision_recommendations = []
            
            for weak_module in weak_modules_list[:3]:  # Top 3 weakest
                # Check if this module is in the user's path and has dependencies
                user_path = _get_learner_path(user_id)
                module_in_path = any(
                    node.get('title') == weak_module['module'] or node.get('id') == weak_module['module'] 
                    for node in user_path
                )
                
                if module_in_path:
                    revision_recommendations.append({
                        "module": weak_module['module'],
                        "current_score": weak_module['score'],
                        "recommendation": "add_revision_before",
                        "priority": "high" if weak_module['score'] < 60 else "medium",
                        "estimated_revision_time": 4,
                        "reason": f"Low quiz performance ({weak_module['score']}%)"
                    })
            
            # Overall success probability assessment
            overall_assessment = "good" if success_prob > 0.7 else "moderate" if success_prob > 0.5 else "poor"
            
            return {
                "user_id": user_id,
                "success_probability": success_prob,
                "overall_assessment": overall_assessment,
                "weak_modules_detected": len(weak_modules_list),
                "revision_recommendations": revision_recommendations,
                "should_add_revision_nodes": len(revision_recommendations) > 0 and success_prob < 0.7
            }
            
        except Exception as e:
            print(f"Error in revision recommendation: {e}")
            return {
                "user_id": user_id,
                "error": str(e),
                "revision_recommendations": []
            }

# ----------------------------
# Interactive Standalone Test
# ----------------------------
if __name__ == "__main__":
    path_service = LearningPathService()
    forecaster = GANForecaster(train_epochs=120,
                              path_service=path_service  )
    learner_id = "learner_001"

    metrics = forecaster.evaluate_path(learner_id)
    import json
    print("\nLearner Path Metrics:")
    print(json.dumps(metrics, indent=2))

    suggestions = forecaster.suggest_skips(learner_id)
    print("\nSuggested Modules to Skip:")
    if suggestions:
        for m in suggestions:
            print(f"- {m}")
    else:
        print("No modules recommended for skipping.")

    path = _get_learner_path(learner_id)
    if path:
        print("\nAvailable Modules:")
        for i, node in enumerate(path, 1):
            print(f"{i}. {node.get('title', node.get('id'))}")

        choice = input("\nEnter the title or ID of the module you want to skip: ").strip()
        if choice:
            result = forecaster.should_skip_module(learner_id, choice)
            print("\nSkip Analysis Result:")
            print(json.dumps(result, indent=2))
        else:
            print("No module selected. Skipping analysis.")

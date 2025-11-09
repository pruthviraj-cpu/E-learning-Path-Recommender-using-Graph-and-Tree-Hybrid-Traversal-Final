import importlib
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Any, Optional, Callable, Tuple

# ----------------------------
# Locate learner-path provider dynamically
# ----------------------------
def _locate_path_fetcher() -> Callable[[str], List[Dict[str, Any]]]:
    mod_name = "path_service"
    try:
        mod = importlib.import_module(mod_name)
    except Exception as e:
        raise ImportError(f"Cannot import module '{mod_name}': {e}")

    for fn_name in ("get_learner_path", "get_learning_path"):
        fn = getattr(mod, fn_name, None)
        if callable(fn):
            return fn

    instance = getattr(mod, "path_service", None)
    if instance is not None:
        for method_name in ("get_learner_path", "get_learning_path"):
            method = getattr(instance, method_name, None)
            if callable(method):
                return method

    raise ImportError("path_service does not expose get_learner_path or get_learning_path.")


_get_learner_path = _locate_path_fetcher()

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
    CORE_MODULES = [
        "Python Basics",
        "Linear Algebra",
        "Statistics & Probability",
        "NumPy & Pandas",
        "Machine Learning Basics"
    ]

    MIN_DIFFICULTY_SPIKE = 1.0
    MIN_SUCCESS_DIFF = 0.05

    def __init__(self,
                 embedding_dim: Optional[int] = None,
                 device: str = "cpu",
                 gen_hidden: int = 64,
                 dis_hidden: int = 64,
                 train_epochs: int = 200):
        self.device = torch.device(device)
        self._static_embedding_dim = embedding_dim
        self.gen_hidden = gen_hidden
        self.dis_hidden = dis_hidden
        self.train_epochs = train_epochs
        self.generator = None
        self.discriminator = None
        self.optim_G = None
        self.optim_D = None
        self.loss_fn = nn.BCELoss()

    # ----------------------------
    # GAN model setup
    # ----------------------------
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
            self.optim_G.step()

    # ----------------------------
    # Core evaluation
    # ----------------------------
    def evaluate_path(self, learner_id: str) -> Dict[str, Any]:
        path = _get_learner_path(learner_id)
        if not path:
            raise ValueError(f"No learner path found for ID: {learner_id}")

        base_embs, dim = self._prepare_embeddings_matrix(path)
        self.train_gan(base_embs)

        with torch.no_grad():
            noise = torch.randn(base_embs.shape[0], dim, device=self.device)
            fake_embs = self.generator(noise).cpu().numpy()

        metrics = self._compute_metrics(path, base_embs, fake_embs)
        metrics["revision_advice"] = self._detect_revision_points(path, metrics)
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
        path = _get_learner_path(learner_id)
        if not path:
            raise ValueError(f"No learner path for {learner_id}")

        # 1 Never skip core modules
        if module_title_or_id in self.CORE_MODULES:
            return {
                "module": module_title_or_id,
                "advice": "This is a foundational module and should not be skipped.",
                "skip_recommended": False
            }

        # 2Check dependency graph
        if self._has_dependents(module_title_or_id, path):
            return {
                "module": module_title_or_id,
                "advice": f"Cannot skip '{module_title_or_id}' because later modules depend on it.",
                "skip_recommended": False
            }

        # 3 Evaluate GAN impact
        base_metrics = self.evaluate_path(learner_id)
        modified_path = [n for n in path if n.get("title") != module_title_or_id and n.get("id") != module_title_or_id]
        if not modified_path:
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

    def suggest_skips(self, learner_id: str) -> List[str]:
        path = _get_learner_path(learner_id)
        suggestions = []
        for node in path:
            module_id = node.get("title") or node.get("id")
            result = self.should_skip_module(learner_id, module_id)
            if result["skip_recommended"]:
                suggestions.append(module_id)
        return suggestions

# ----------------------------
# Interactive Standalone Test
# ----------------------------
if __name__ == "__main__":
    forecaster = GANForecaster(train_epochs=120)
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

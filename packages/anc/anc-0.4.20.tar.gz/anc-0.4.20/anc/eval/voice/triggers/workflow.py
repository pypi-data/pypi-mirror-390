import os
import time

from ...utils import invoke_evaluation_service, collect_specific_repos
from ...utils import rank_zero_only

class AncOmniHarnessEvalTrigger():
    def __init__(self, 
                 tasks, 
                 batch_size,
                 save_path,
                 model_name,
                 tokenizer_path,
                 seq_length,
                 wandb_project,
                 wandb_api_key,
                 anc_omni_git_commit,
                 harness_git_commit,
                 tp=1,
                 pp=1):
        
        self.project = "voice"
        self.tp = tp
        self.pp = pp
        self.seq_length = seq_length
        self.save_path = save_path
        self.model_name = model_name
        self.batch_size = batch_size
        self.cluster = os.getenv("MLP_CLUSTER", "va")
        self.project = os.getenv("MLP_PROJECT", "voice")
        self.tasks = tasks
        self.start_time = time.time()
        self.wandb_project = wandb_project
        self.wandb_api_key = wandb_api_key
        self.tokenizer_path = tokenizer_path
        self.project_name = os.path.basename(os.path.normpath(self.save_path))
        self.anc_omni_git_commit = anc_omni_git_commit
        self.harness_git_commit = harness_git_commit

    @rank_zero_only
    def trigger(self, model_path, steps):
        """
        Trigger an evaluation by sending a POST request to the model management server.

        Args:
            model_path (str, optional): Override the model path. If None, uses args.model_path or checkpoint path
        """
        # Allow override of model_path and version_name
        assert model_path is not None, "model_path is required"

        # Prepare the payload
        payload = {
            "project": self.project,
            "project_name": self.project_name,
            "model_name": self.model_name,
            "cluster": self.cluster,
            "eval_tp": self.tp,
            "eval_pp": self.pp,
            "eval_seqlen": self.seq_length,
            "eval_batch_size": self.batch_size,
            "eval_ckpt_list": [model_path],
            "eval_tasks": self.tasks,
            "eval_tokenizer_path": self.tokenizer_path,
            "project": "voice",
            "train_steps": steps,
            "code_info": {
                "ANC_OMNI": {
                    "commit": self.anc_omni_git_commit
                },
                "LM_EVALUATION_HARNESS": {
                    "commit": self.harness_git_commit
                }
            }
        }

        if os.getenv("WANDB_MODE") != "disabled":
            payload["wandb_project"] = self.wandb_project
            payload["wandb_api_key"] = self.wandb_api_key

        print(f"auto eval trigger payload: {payload}")

        return invoke_evaluation_service(payload, "evaluations")

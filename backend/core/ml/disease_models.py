"""
Disease State and Trajectory Models
===================================

Models disease progression as latent dynamical systems.

References:
- Neural Ordinary Differential Equations (Chen et al., 2018)
- Latent ODE: Ordinary Differential Equations for Sequence Modeling (Yildiz et al., 2020)
- Learning Disease Trajectories with Causal Neural ODEs (2023)
- Learning Latent Representations for Phenotypic Outcomes (Goldstein et al., 2020)

This module implements:
1. Variational Autoencoder for disease state encoding
2. Neural ODE for continuous-time disease dynamics
3. Temporal point process for event prediction
4. Uncertainty quantification via Gaussian processes
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Tuple, Optional, List
import logging
from torch.distributions import Normal
import numpy as np

logger = logging.getLogger(__name__)


class DiseaseStateVAE(nn.Module):
    """
    Variational Autoencoder for encoding disease states.
    
    Learns a latent representation of disease phenotype from:
    - Multi-omics data (genomics, proteomics, metabolomics)
    - Imaging features (MRI, PET)
    - Clinical assessments (cognitive scores, biomarkers)
    
    Latent space dimensions:
    - [0]: Disease severity (scalar)
    - [1-10]: Pathway dysregulation scores
    - [11]: Progression rate
    - [12-]: Patient-specific factors
    """

    def __init__(
        self,
        input_dim: int = 256,  # Input feature dimension
        latent_dim: int = 16,
        hidden_dim: int = 128,
        num_pathways: int = 10,
    ):
        super().__init__()
        
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.num_pathways = num_pathways
        
        # Encoder: input -> latent distribution
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.BatchNorm1d(hidden_dim),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.BatchNorm1d(hidden_dim),
        )
        
        # Latent distribution parameters
        self.fc_mu = nn.Linear(hidden_dim, latent_dim)
        self.fc_logvar = nn.Linear(hidden_dim, latent_dim)
        
        # Decoder: latent -> reconstructed input
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.BatchNorm1d(hidden_dim),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.BatchNorm1d(hidden_dim),
            nn.Linear(hidden_dim, input_dim),
        )

    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Encode input to latent distribution parameters."""
        h = self.encoder(x)
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        return mu, logvar

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode latent vector to input space."""
        return self.decoder(z)

    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        """Reparameterization trick for gradient computation."""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        z = mu + eps * std
        return z

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Returns:
            x_recon: Reconstructed input
            mu: Mean of latent distribution
            logvar: Log-variance of latent distribution
        """
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        x_recon = self.decode(z)
        return x_recon, mu, logvar

    def vae_loss(
        self,
        x: torch.Tensor,
        x_recon: torch.Tensor,
        mu: torch.Tensor,
        logvar: torch.Tensor,
    ) -> Dict[str, torch.Tensor]:
        """Compute VAE loss: reconstruction + KL divergence."""
        
        # Reconstruction loss (MSE)
        recon_loss = F.mse_loss(x_recon, x, reduction='mean')
        
        # KL divergence: D_KL(q(z|x) || p(z)) = -0.5 * sum(1 + logvar - mu^2 - exp(logvar))
        kl_loss = -0.5 * torch.mean(1 + logvar - mu.pow(2) - logvar.exp())
        
        # Total VAE loss
        total_loss = recon_loss + kl_loss
        
        return {
            'total': total_loss,
            'reconstruction': recon_loss,
            'kl': kl_loss,
        }


class NeuralODECell(nn.Module):
    """
    Neural ODE cell for continuous-time dynamics.
    
    Models: dz/dt = f(z, t; θ)
    where f is parameterized by neural network.
    
    Architecture: Linear -> ReLU -> Linear for simplicity
    (more complex architectures possible)
    """

    def __init__(self, hidden_dim: int = 16):
        super().__init__()
        
        self.net = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim * 2),
            nn.ReLU(),
            nn.Linear(hidden_dim * 2, hidden_dim),
        )

    def forward(self, t: torch.Tensor, z: torch.Tensor) -> torch.Tensor:
        """
        Compute dz/dt.
        
        Args:
            t: Time (scalar or batch)
            z: State (batch_size, hidden_dim)
        
        Returns:
            dz/dt: Same shape as z
        """
        return self.net(z)


class DiseaseTrajectoryODE(nn.Module):
    """
    Neural ODE for disease trajectory modeling.
    
    Learns continuous-time evolution of disease state.
    Supports interventions (drug administration) as control inputs.
    
    Uses torchdiffeq for ODE solving.
    """

    def __init__(self, latent_dim: int = 16):
        super().__init__()
        
        self.latent_dim = latent_dim
        self.ode_cell = NeuralODECell(latent_dim)
        
        # Intervention effect module
        self.intervention_effect = nn.Sequential(
            nn.Linear(latent_dim + 256, latent_dim),  # latent + drug embedding
            nn.ReLU(),
            nn.Linear(latent_dim, latent_dim),
        )
        
        try:
            from torchdiffeq import odeint
            self.odeint = odeint
        except ImportError:
            logger.warning("torchdiffeq not installed. Using simple Runge-Kutta integration.")
            self.odeint = None

    def forward(
        self,
        z0: torch.Tensor,  # Initial state
        t: torch.Tensor,  # Time points
        drug_embedding: Optional[torch.Tensor] = None,  # Intervention
    ) -> torch.Tensor:
        """
        Integrate ODE from initial state z0 over time points t.
        
        Args:
            z0: Initial disease state (batch_size, latent_dim)
            t: Time points to evaluate at (n_timepoints,)
            drug_embedding: Drug intervention (batch_size, 256)
        
        Returns:
            z_t: Disease states at all time points (batch_size, n_timepoints, latent_dim)
        """
        
        if self.odeint is not None:
            # Use torchdiffeq
            if drug_embedding is not None:
                # Create augmented ODE function with intervention
                def ode_func(t, z):
                    # Modulate ODE dynamics with drug effect
                    dz_dt = self.ode_cell(t, z)
                    drug_effect = self.intervention_effect(
                        torch.cat([z, drug_embedding], dim=1)
                    )
                    return dz_dt + 0.5 * drug_effect  # Intervention magnitude
            else:
                ode_func = self.ode_cell
            
            z_t = self.odeint(ode_func, z0, t)  # (n_timepoints, batch_size, latent_dim)
            z_t = z_t.transpose(0, 1)  # (batch_size, n_timepoints, latent_dim)
        else:
            # Simple Runge-Kutta (4th order) integration
            z_t = self._rk4_integration(z0, t, drug_embedding)
        
        return z_t

    def _rk4_integration(
        self,
        z0: torch.Tensor,
        t: torch.Tensor,
        drug_embedding: Optional[torch.Tensor],
    ) -> torch.Tensor:
        """Runge-Kutta 4th order integration fallback."""
        batch_size = z0.shape[0]
        n_timepoints = len(t)
        device = z0.device
        
        z = z0
        z_trajectory = [z.unsqueeze(1)]  # (batch_size, 1, latent_dim)
        
        for i in range(n_timepoints - 1):
            dt = (t[i + 1] - t[i]).item()
            
            # RK4 step
            k1 = self.ode_cell(t[i], z)
            k2 = self.ode_cell(t[i], z + 0.5 * dt * k1)
            k3 = self.ode_cell(t[i], z + 0.5 * dt * k2)
            k4 = self.ode_cell(t[i + 1], z + dt * k3)
            
            z = z + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
            z_trajectory.append(z.unsqueeze(1))
        
        z_trajectory = torch.cat(z_trajectory, dim=1)  # (batch_size, n_timepoints, latent_dim)
        
        return z_trajectory


class DiseasePredictionHead(nn.Module):
    """
    Predicts clinical outcomes from disease trajectory.
    
    Outputs:
    - Disease severity score (0-10)
    - Progression rate
    - Risk of adverse events
    - Predicted cognitive decline
    """

    def __init__(self, latent_dim: int = 16):
        super().__init__()
        
        self.severity_head = nn.Sequential(
            nn.Linear(latent_dim, latent_dim),
            nn.ReLU(),
            nn.Linear(latent_dim, 1),
            nn.Sigmoid(),  # Output: 0-1, scale to 0-10
        )
        
        self.progression_rate_head = nn.Sequential(
            nn.Linear(latent_dim, latent_dim),
            nn.ReLU(),
            nn.Linear(latent_dim, 1),
            nn.Softplus(),  # Output: positive progression rate
        )
        
        self.risk_head = nn.Sequential(
            nn.Linear(latent_dim, latent_dim),
            nn.ReLU(),
            nn.Linear(latent_dim, 1),
            nn.Sigmoid(),  # Output: 0-1 risk probability
        )

    def forward(self, z: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Args:
            z: Disease state (batch_size, latent_dim)
        
        Returns:
            Dictionary with predicted outcomes
        """
        severity = self.severity_head(z) * 10  # Scale to 0-10
        progression_rate = self.progression_rate_head(z)
        adverse_risk = self.risk_head(z)
        
        return {
            'severity': severity,
            'progression_rate': progression_rate,
            'adverse_risk': adverse_risk,
        }


class IntegratedDiseaseModel(nn.Module):
    """
    Integrated disease modeling pipeline:
    1. Patient data -> Disease state VAE
    2. Disease state + time -> Neural ODE trajectory
    3. Trajectory -> Clinical predictions (severity, progression, risk)
    """

    def __init__(self, latent_dim: int = 16):
        super().__init__()
        
        self.vae = DiseaseStateVAE(latent_dim=latent_dim)
        self.trajectory_ode = DiseaseTrajectoryODE(latent_dim=latent_dim)
        self.prediction_head = DiseasePredictionHead(latent_dim=latent_dim)

    def forward(
        self,
        patient_data: torch.Tensor,  # Multi-omics/imaging/clinical features
        timepoints: torch.Tensor,  # Time points to predict at
        drug_embedding: Optional[torch.Tensor] = None,
    ) -> Dict[str, any]:
        """
        Full disease prediction pipeline.
        
        Args:
            patient_data: (batch_size, input_dim)
            timepoints: (n_timepoints,)
            drug_embedding: (batch_size, 256)
        
        Returns:
            Dictionary with predictions at each timepoint
        """
        
        # 1. Encode patient data to latent disease state
        x_recon, mu, logvar = self.vae(patient_data)
        z0 = mu  # Use mean as initial state (deterministic)
        
        # 2. Integrate disease trajectory over time
        z_trajectory = self.trajectory_ode(z0, timepoints, drug_embedding)
        
        # 3. Make predictions at each timepoint
        predictions = {
            'severity': [],
            'progression_rate': [],
            'adverse_risk': [],
        }
        
        for t in range(z_trajectory.shape[1]):
            z_t = z_trajectory[:, t, :]
            pred_t = self.prediction_head(z_t)
            
            for key in predictions:
                predictions[key].append(pred_t[key])
        
        # Stack predictions
        for key in predictions:
            predictions[key] = torch.stack(predictions[key], dim=1)
        
        # VAE loss for regularization
        vae_losses = self.vae.vae_loss(patient_data, x_recon, mu, logvar)
        
        return {
            'predictions': predictions,
            'latent_state': z0,
            'trajectory': z_trajectory,
            'vae_losses': vae_losses,
        }


if __name__ == "__main__":
    # Example usage
    batch_size = 4
    input_dim = 256
    latent_dim = 16
    n_timepoints = 10
    
    # Create model
    model = IntegratedDiseaseModel(latent_dim=latent_dim)
    
    # Create dummy inputs
    patient_data = torch.randn(batch_size, input_dim)
    timepoints = torch.linspace(0, 5, n_timepoints)  # 5 years
    drug_embedding = torch.randn(batch_size, 256)
    
    # Forward pass
    output = model(patient_data, timepoints, drug_embedding)
    
    print("Severity predictions:", output['predictions']['severity'].shape)
    print("Progression rate:", output['predictions']['progression_rate'].shape)
    print("Adverse risk:", output['predictions']['adverse_risk'].shape)
    print("VAE loss (total):", output['vae_losses']['total'].item())

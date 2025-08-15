#!/usr/bin/env python3
"""
🎨 LIVE TRAINING VISUALIZATION - Real-time gorgeous plots
Ultra-sexy training dashboard for TEKNOFEST 2025
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import seaborn as sns
import numpy as np
from datetime import datetime
from IPython.display import display, clear_output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from transformers import TrainerCallback
import time

# Set beautiful style
plt.style.use('dark_background')
sns.set_palette("husl")

class LiveTrainingVisualizer(TrainerCallback):
    """
    🎨 ULTRA SEXY LIVE TRAINING VISUALIZER
    Real-time plots that update every step!
    """
    
    def __init__(self, update_freq=1):
        self.update_freq = update_freq
        self.losses = []
        self.lrs = []
        self.steps = []
        self.gradients = []
        self.timestamps = []
        self.best_loss = float('inf')
        self.best_step = 0
        
        # Initialize figure
        self.setup_dashboard()
        
    def setup_dashboard(self):
        """Create sexy dashboard layout"""
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.patch.set_facecolor('#0E1117')
        
        # Create grid
        gs = self.fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Main loss plot (large)
        self.ax_loss = self.fig.add_subplot(gs[0:2, 0:2])
        self.ax_loss.set_facecolor('#1E1E1E')
        
        # Learning rate plot
        self.ax_lr = self.fig.add_subplot(gs[0, 2])
        self.ax_lr.set_facecolor('#1E1E1E')
        
        # Loss distribution
        self.ax_dist = self.fig.add_subplot(gs[1, 2])
        self.ax_dist.set_facecolor('#1E1E1E')
        
        # Progress bar
        self.ax_progress = self.fig.add_subplot(gs[2, :])
        self.ax_progress.set_facecolor('#1E1E1E')
        
        plt.suptitle('🚀 TEKNOFEST 2025 - LIVE TRAINING DASHBOARD', 
                     fontsize=16, fontweight='bold', color='#00D4FF')
        
    def on_log(self, args, state, control, logs=None, **kwargs):
        """Update visualizations on each log"""
        
        if logs and state.global_step % self.update_freq == 0:
            # Collect data
            if 'loss' in logs:
                self.losses.append(logs['loss'])
                self.steps.append(state.global_step)
                self.timestamps.append(datetime.now())
                
                if 'learning_rate' in logs:
                    self.lrs.append(logs['learning_rate'])
                else:
                    self.lrs.append(self.lrs[-1] if self.lrs else 5e-5)
                
                # Track best
                if logs['loss'] < self.best_loss:
                    self.best_loss = logs['loss']
                    self.best_step = state.global_step
                
                # Update plots
                self.update_plots(state, args)
    
    def update_plots(self, state, args):
        """Update all plots with sexy animations"""
        clear_output(wait=True)
        
        # Clear all axes
        self.ax_loss.clear()
        self.ax_lr.clear()
        self.ax_dist.clear()
        self.ax_progress.clear()
        
        # 1. MAIN LOSS PLOT with gradient fill
        if len(self.losses) > 0:
            self.ax_loss.plot(self.steps, self.losses, 
                            color='#00D4FF', linewidth=2.5, 
                            label='Training Loss', alpha=0.9)
            
            # Add gradient fill
            self.ax_loss.fill_between(self.steps, self.losses, 
                                     alpha=0.3, color='#00D4FF')
            
            # Mark best point
            self.ax_loss.scatter([self.best_step], [self.best_loss], 
                               color='#FFD700', s=100, zorder=5,
                               marker='⭐', label=f'Best: {self.best_loss:.4f}')
            
            # Add smooth trend line
            if len(self.losses) > 5:
                z = np.polyfit(self.steps, self.losses, 3)
                p = np.poly1d(z)
                smooth_steps = np.linspace(self.steps[0], self.steps[-1], 100)
                self.ax_loss.plot(smooth_steps, p(smooth_steps), 
                                '--', color='#FF6B6B', alpha=0.5, 
                                label='Trend', linewidth=1.5)
            
            self.ax_loss.set_title('📊 Training Loss Evolution', 
                                  fontsize=12, fontweight='bold', color='white')
            self.ax_loss.set_xlabel('Steps', color='gray')
            self.ax_loss.set_ylabel('Loss', color='gray')
            self.ax_loss.grid(True, alpha=0.2, linestyle='--')
            self.ax_loss.legend(loc='upper right')
            
            # Add annotations
            current_loss = self.losses[-1]
            improvement = ((self.losses[0] - current_loss) / self.losses[0] * 100) if self.losses[0] > 0 else 0
            self.ax_loss.text(0.02, 0.98, f'Current: {current_loss:.4f}\nImprovement: {improvement:.1f}%',
                            transform=self.ax_loss.transAxes,
                            fontsize=10, verticalalignment='top',
                            bbox=dict(boxstyle='round', facecolor='#2E2E2E', alpha=0.8))
        
        # 2. LEARNING RATE PLOT with glow effect
        if len(self.lrs) > 0:
            self.ax_lr.plot(self.steps, self.lrs, 
                          color='#FF6EC7', linewidth=2.5, 
                          marker='o', markersize=3)
            self.ax_lr.fill_between(self.steps, self.lrs, 
                                   alpha=0.3, color='#FF6EC7')
            
            self.ax_lr.set_title('🎯 Learning Rate', fontsize=10, color='white')
            self.ax_lr.set_xlabel('Steps', fontsize=8, color='gray')
            self.ax_lr.set_ylabel('LR', fontsize=8, color='gray')
            self.ax_lr.set_yscale('log')
            self.ax_lr.grid(True, alpha=0.2, linestyle='--')
            
            # Add current LR text
            current_lr = self.lrs[-1]
            self.ax_lr.text(0.5, 0.95, f'{current_lr:.2e}',
                          transform=self.ax_lr.transAxes,
                          fontsize=14, fontweight='bold',
                          horizontalalignment='center',
                          color='#FF6EC7')
        
        # 3. LOSS DISTRIBUTION (last 20 values)
        if len(self.losses) > 1:
            recent_losses = self.losses[-20:]
            self.ax_dist.hist(recent_losses, bins=10, 
                            color='#4ECDC4', alpha=0.7, 
                            edgecolor='white', linewidth=1)
            
            # Add mean line
            mean_loss = np.mean(recent_losses)
            self.ax_dist.axvline(mean_loss, color='#FFD700', 
                               linestyle='--', linewidth=2, 
                               label=f'Mean: {mean_loss:.4f}')
            
            self.ax_dist.set_title('📈 Recent Loss Distribution', 
                                 fontsize=10, color='white')
            self.ax_dist.set_xlabel('Loss', fontsize=8, color='gray')
            self.ax_dist.set_ylabel('Count', fontsize=8, color='gray')
            self.ax_dist.legend(loc='upper right', fontsize=8)
            self.ax_dist.grid(True, alpha=0.2, axis='y')
        
        # 4. PROGRESS BAR with gradient
        progress = state.global_step / args.max_steps
        
        # Create gradient progress bar
        gradient = np.linspace(0, 1, 100).reshape(1, -1)
        extent = [0, args.max_steps, 0, 1]
        
        self.ax_progress.imshow(gradient, aspect='auto', 
                               cmap='cool', extent=extent, alpha=0.3)
        
        # Add filled progress
        filled_width = state.global_step
        rect = Rectangle((0, 0), filled_width, 1, 
                        facecolor='#00D4FF', alpha=0.8)
        self.ax_progress.add_patch(rect)
        
        # Add markers for checkpoints
        checkpoint_steps = [i for i in self.steps if i % args.save_steps == 0]
        for cp_step in checkpoint_steps:
            self.ax_progress.axvline(cp_step, color='#FFD700', 
                                    alpha=0.5, linewidth=1)
        
        # Progress text
        self.ax_progress.text(args.max_steps/2, 0.5, 
                            f'{state.global_step}/{args.max_steps} ({progress*100:.1f}%)',
                            horizontalalignment='center', 
                            verticalalignment='center',
                            fontsize=14, fontweight='bold', color='white')
        
        # Time estimation
        if len(self.timestamps) > 1:
            elapsed = (self.timestamps[-1] - self.timestamps[0]).total_seconds()
            steps_done = self.steps[-1] - self.steps[0]
            if steps_done > 0:
                time_per_step = elapsed / steps_done
                remaining_steps = args.max_steps - state.global_step
                eta_seconds = remaining_steps * time_per_step
                eta_min = int(eta_seconds // 60)
                eta_sec = int(eta_seconds % 60)
                
                self.ax_progress.text(0.02, 0.5, f'ETA: {eta_min}m {eta_sec}s',
                                    transform=self.ax_progress.transAxes,
                                    fontsize=10, color='gray')
        
        self.ax_progress.set_xlim(0, args.max_steps)
        self.ax_progress.set_ylim(0, 1)
        self.ax_progress.set_title('🏃 Training Progress', fontsize=10, color='white')
        self.ax_progress.set_xlabel('Steps', fontsize=8, color='gray')
        self.ax_progress.set_yticks([])
        
        # Add stats panel
        self.fig.text(0.99, 0.01, 
                     f'Updated: {datetime.now().strftime("%H:%M:%S")}',
                     horizontalalignment='right',
                     fontsize=8, color='gray')
        
        plt.tight_layout()
        display(self.fig)


class InteractivePlotlyDashboard(TrainerCallback):
    """
    📊 INTERACTIVE PLOTLY DASHBOARD
    Even sexier with interactive plots!
    """
    
    def __init__(self, update_freq=5):
        self.update_freq = update_freq
        self.data = {
            'step': [],
            'loss': [],
            'lr': [],
            'time': [],
            'gradient_norm': []
        }
        self.fig = None
        
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs and state.global_step % self.update_freq == 0:
            # Collect data
            self.data['step'].append(state.global_step)
            self.data['loss'].append(logs.get('loss', 0))
            self.data['lr'].append(logs.get('learning_rate', 0))
            self.data['time'].append(datetime.now())
            self.data['gradient_norm'].append(logs.get('grad_norm', 0))
            
            # Update dashboard
            self.update_dashboard(state, args)
    
    def update_dashboard(self, state, args):
        """Create interactive Plotly dashboard"""
        clear_output(wait=True)
        
        # Create subplots
        self.fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('📉 Loss Curve', '🎯 Learning Rate', 
                          '📊 Loss Smoothing', '⚡ Training Speed'),
            specs=[[{'secondary_y': False}, {'secondary_y': False}],
                   [{'secondary_y': False}, {'secondary_y': False}]]
        )
        
        # 1. Loss curve with hover
        self.fig.add_trace(
            go.Scatter(x=self.data['step'], y=self.data['loss'],
                      mode='lines+markers',
                      name='Loss',
                      line=dict(color='#00D4FF', width=3),
                      marker=dict(size=6, color='#00D4FF'),
                      hovertemplate='Step: %{x}<br>Loss: %{y:.4f}'),
            row=1, col=1
        )
        
        # Add best point
        if self.data['loss']:
            best_idx = np.argmin(self.data['loss'])
            self.fig.add_trace(
                go.Scatter(x=[self.data['step'][best_idx]], 
                          y=[self.data['loss'][best_idx]],
                          mode='markers',
                          marker=dict(size=15, color='gold', symbol='star'),
                          name=f'Best: {self.data["loss"][best_idx]:.4f}',
                          showlegend=True),
                row=1, col=1
            )
        
        # 2. Learning rate
        self.fig.add_trace(
            go.Scatter(x=self.data['step'], y=self.data['lr'],
                      mode='lines+markers',
                      name='Learning Rate',
                      line=dict(color='#FF6EC7', width=2),
                      marker=dict(size=5)),
            row=1, col=2
        )
        
        # 3. Smoothed loss (moving average)
        if len(self.data['loss']) > 5:
            window = min(10, len(self.data['loss']))
            smoothed = pd.Series(self.data['loss']).rolling(window, min_periods=1).mean()
            
            self.fig.add_trace(
                go.Scatter(x=self.data['step'], y=self.data['loss'],
                          mode='lines',
                          name='Raw',
                          line=dict(color='#4ECDC4', width=1),
                          opacity=0.3),
                row=2, col=1
            )
            
            self.fig.add_trace(
                go.Scatter(x=self.data['step'], y=smoothed,
                          mode='lines',
                          name='Smoothed',
                          line=dict(color='#4ECDC4', width=3)),
                row=2, col=1
            )
        
        # 4. Training speed (steps per minute)
        if len(self.data['time']) > 1:
            time_diffs = [(self.data['time'][i] - self.data['time'][i-1]).total_seconds() 
                         for i in range(1, len(self.data['time']))]
            steps_per_sec = [1/t if t > 0 else 0 for t in time_diffs]
            steps_per_min = [s * 60 for s in steps_per_sec]
            
            self.fig.add_trace(
                go.Scatter(x=self.data['step'][1:], y=steps_per_min,
                          mode='lines',
                          fill='tozeroy',
                          name='Steps/min',
                          line=dict(color='#95E77E', width=2)),
                row=2, col=2
            )
        
        # Update layout
        self.fig.update_layout(
            template='plotly_dark',
            title=dict(text=f'<b>🚀 TEKNOFEST 2025 Training Dashboard</b><br>Step {state.global_step}/{args.max_steps}',
                      font=dict(size=20)),
            showlegend=True,
            height=700,
            hovermode='x unified'
        )
        
        # Update axes
        self.fig.update_xaxes(title_text="Steps", gridcolor='#2E2E2E')
        self.fig.update_yaxes(gridcolor='#2E2E2E')
        self.fig.update_yaxes(title_text="Loss", row=1, col=1)
        self.fig.update_yaxes(title_text="LR", type="log", row=1, col=2)
        self.fig.update_yaxes(title_text="Loss", row=2, col=1)
        self.fig.update_yaxes(title_text="Steps/min", row=2, col=2)
        
        # Show
        self.fig.show()


# Colab-specific cell to add to notebook:
COLAB_VISUALIZATION_CELL = '''
# Add this cell for SEXY LIVE VISUALIZATION

# Install required
!pip install plotly -q

from IPython.display import display, clear_output
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

class SexyLiveTrainingViz(TrainerCallback):
    """Ultra sexy training visualization"""
    
    def __init__(self):
        self.losses = []
        self.lrs = []
        self.steps = []
        self.best_loss = float('inf')
        
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs and 'loss' in logs:
            # Collect data
            self.losses.append(logs['loss'])
            self.steps.append(state.global_step)
            self.lrs.append(logs.get('learning_rate', 5e-5))
            
            if logs['loss'] < self.best_loss:
                self.best_loss = logs['loss']
            
            # Update plot every step
            if state.global_step % 1 == 0:
                self.update_plot(state, args)
    
    def update_plot(self, state, args):
        clear_output(wait=True)
        
        # Create figure with dark theme
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 8))
        fig.patch.set_facecolor('#0E1117')
        
        # Style all axes
        for ax in [ax1, ax2, ax3, ax4]:
            ax.set_facecolor('#1E1E1E')
            ax.grid(True, alpha=0.2, color='gray', linestyle='--')
            ax.spines['bottom'].set_color('gray')
            ax.spines['top'].set_color('gray')
            ax.spines['left'].set_color('gray')
            ax.spines['right'].set_color('gray')
            ax.tick_params(colors='gray')
            ax.xaxis.label.set_color('gray')
            ax.yaxis.label.set_color('gray')
        
        # 1. Loss curve
        ax1.plot(self.steps, self.losses, color='#00D4FF', linewidth=2.5, alpha=0.9)
        ax1.fill_between(self.steps, self.losses, alpha=0.3, color='#00D4FF')
        ax1.scatter(self.steps[-1], self.losses[-1], color='#FFD700', s=100, zorder=5)
        ax1.set_title('📉 Training Loss', color='white', fontweight='bold', fontsize=12)
        ax1.set_xlabel('Steps')
        ax1.set_ylabel('Loss')
        
        # Add text annotations
        ax1.text(0.02, 0.98, f'Current: {self.losses[-1]:.4f}\\nBest: {self.best_loss:.4f}',
                transform=ax1.transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='#2E2E2E', alpha=0.8),
                color='white')
        
        # 2. Learning rate
        ax2.plot(self.steps, self.lrs, color='#FF6EC7', linewidth=2, marker='o', markersize=3)
        ax2.set_title('🎯 Learning Rate', color='white', fontweight='bold', fontsize=12)
        ax2.set_xlabel('Steps')
        ax2.set_ylabel('LR')
        ax2.set_yscale('log')
        
        # 3. Loss change rate
        if len(self.losses) > 1:
            loss_changes = [self.losses[i] - self.losses[i-1] for i in range(1, len(self.losses))]
            ax3.bar(self.steps[1:], loss_changes, color=np.where(np.array(loss_changes) < 0, '#4ECDC4', '#FF6B6B'), alpha=0.7)
            ax3.axhline(y=0, color='white', linestyle='-', linewidth=0.5)
            ax3.set_title('📊 Loss Change per Step', color='white', fontweight='bold', fontsize=12)
            ax3.set_xlabel('Steps')
            ax3.set_ylabel('Δ Loss')
        
        # 4. Progress bar
        progress = state.global_step / args.max_steps
        ax4.barh([0], [progress], height=0.5, color='#00D4FF', alpha=0.8)
        ax4.barh([0], [1-progress], left=[progress], height=0.5, color='#2E2E2E', alpha=0.5)
        ax4.set_xlim(0, 1)
        ax4.set_ylim(-0.5, 0.5)
        ax4.set_title(f'🏃 Progress: {state.global_step}/{args.max_steps} ({progress*100:.1f}%)', 
                     color='white', fontweight='bold', fontsize=12)
        ax4.set_yticks([])
        ax4.set_xlabel('Completion')
        
        # Add ETA
        if len(self.steps) > 1:
            steps_per_log = self.steps[-1] - self.steps[-2]
            remaining = args.max_steps - state.global_step
            eta_logs = remaining / steps_per_log if steps_per_log > 0 else 0
            ax4.text(0.5, -0.3, f'ETA: ~{int(eta_logs)} logs', 
                    ha='center', color='gray', fontsize=10)
        
        plt.suptitle('🚀 TEKNOFEST 2025 - LIVE TRAINING', 
                    fontsize=16, fontweight='bold', color='#00D4FF', y=1.02)
        
        plt.tight_layout()
        plt.show()
        
        # Print status
        print("="*60)
        print(f"⚡ Step {state.global_step} | Loss: {self.losses[-1]:.4f} | LR: {self.lrs[-1]:.2e}")
        print(f"📈 Improvement: {((self.losses[0] - self.losses[-1])/self.losses[0]*100):.1f}%")
        print("="*60)

# Add to trainer callbacks
viz_callback = SexyLiveTrainingViz()

# Update trainer initialization
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    packing=False,
    args=training_args,
    callbacks=[save_callback, lr_callback, emergency_callback, viz_callback],  # Added viz
)

print("✅ Live visualization enabled! Watch the sexy plots update in real-time!")
'''

print("\n" + "="*70)
print("📊 LIVE VISUALIZATION READY!")
print("="*70)
print("\nAdd the visualization callback to see:")
print("  • Real-time loss curves")
print("  • Learning rate changes")
print("  • Progress tracking")
print("  • ETA calculation")
print("  • Best checkpoint tracking")
print("\nUpdates EVERY STEP for maximum sexiness! 🔥")
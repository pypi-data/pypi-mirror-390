"""
Tests for training API functionality.

This module tests the training capabilities of pytensorlogic,
including loss functions, optimizers, callbacks, and the Trainer class.
"""

import json
import numpy as np
import pytest

# Import will work after maturin develop
try:
    import pytensorlogic as tl
    TENSORLOGIC_AVAILABLE = True
except ImportError:
    TENSORLOGIC_AVAILABLE = False
    pytest.skip("pytensorlogic not installed", allow_module_level=True)


class TestLossFunctions:
    """Tests for loss functions."""

    def test_mse_loss_creation(self):
        """Test creating MSE loss function."""
        loss_fn = tl.mse_loss()
        assert loss_fn.loss_type == "mse"

    def test_bce_loss_creation(self):
        """Test creating BCE loss function."""
        loss_fn = tl.bce_loss()
        assert loss_fn.loss_type == "bce"

    def test_cross_entropy_loss_creation(self):
        """Test creating cross-entropy loss function."""
        loss_fn = tl.cross_entropy_loss()
        assert loss_fn.loss_type == "cross_entropy"

    def test_mse_computation(self):
        """Test MSE loss computation."""
        loss_fn = tl.mse_loss()

        predictions = np.array([1.0, 2.0, 3.0])
        targets = np.array([1.0, 2.0, 3.0])

        loss = loss_fn(predictions, targets)
        assert abs(loss - 0.0) < 1e-6  # Perfect predictions

    def test_mse_with_error(self):
        """Test MSE with non-zero error."""
        loss_fn = tl.mse_loss()

        predictions = np.array([1.0, 2.0, 3.0])
        targets = np.array([2.0, 3.0, 4.0])

        loss = loss_fn(predictions, targets)
        assert loss > 0  # Should have positive loss
        assert abs(loss - 1.0) < 1e-6  # MSE = mean((1,1,1)^2) = 1

    def test_bce_computation(self):
        """Test BCE loss computation."""
        loss_fn = tl.bce_loss()

        predictions = np.array([0.5, 0.5])
        targets = np.array([1.0, 0.0])

        loss = loss_fn(predictions, targets)
        assert loss > 0  # Should have positive loss

    def test_cross_entropy_computation(self):
        """Test cross-entropy loss computation."""
        loss_fn = tl.cross_entropy_loss()

        # One-hot targets
        predictions = np.array([[0.7, 0.2, 0.1], [0.1, 0.8, 0.1]])
        targets = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])

        loss = loss_fn(predictions, targets)
        assert loss >= 0  # Cross-entropy is non-negative

    def test_loss_shape_mismatch(self):
        """Test loss function with shape mismatch."""
        loss_fn = tl.mse_loss()

        predictions = np.array([1.0, 2.0, 3.0])
        targets = np.array([1.0, 2.0])  # Different shape

        with pytest.raises(ValueError, match="Shape mismatch"):
            loss_fn(predictions, targets)

    def test_loss_repr(self):
        """Test loss function string representation."""
        loss_fn = tl.mse_loss()
        repr_str = repr(loss_fn)
        assert "LossFunction" in repr_str
        assert "mse" in repr_str


class TestOptimizers:
    """Tests for optimizers."""

    def test_sgd_creation(self):
        """Test creating SGD optimizer."""
        optimizer = tl.sgd(learning_rate=0.01)
        assert optimizer.optimizer_type == "sgd"
        assert abs(optimizer.learning_rate - 0.01) < 1e-9

    def test_sgd_with_momentum(self):
        """Test SGD with momentum."""
        optimizer = tl.sgd(learning_rate=0.01, momentum=0.9)
        assert optimizer.optimizer_type == "sgd"

    def test_adam_creation(self):
        """Test creating Adam optimizer."""
        optimizer = tl.adam()
        assert optimizer.optimizer_type == "adam"
        assert abs(optimizer.learning_rate - 0.001) < 1e-9

    def test_adam_custom_params(self):
        """Test Adam with custom parameters."""
        optimizer = tl.adam(learning_rate=0.01, beta1=0.8, beta2=0.99)
        assert optimizer.optimizer_type == "adam"
        assert abs(optimizer.learning_rate - 0.01) < 1e-9

    def test_rmsprop_creation(self):
        """Test creating RMSprop optimizer."""
        optimizer = tl.rmsprop()
        assert optimizer.optimizer_type == "rmsprop"

    def test_optimizer_learning_rate_setter(self):
        """Test setting learning rate."""
        optimizer = tl.adam(learning_rate=0.001)
        assert abs(optimizer.learning_rate - 0.001) < 1e-9

        optimizer.learning_rate = 0.01
        assert abs(optimizer.learning_rate - 0.01) < 1e-9

    def test_optimizer_repr(self):
        """Test optimizer string representation."""
        optimizer = tl.adam(learning_rate=0.001)
        repr_str = repr(optimizer)
        assert "Optimizer" in repr_str
        assert "adam" in repr_str


class TestCallbacks:
    """Tests for callbacks."""

    def test_early_stopping_creation(self):
        """Test creating EarlyStopping callback."""
        callback = tl.early_stopping()
        assert callback.callback_type == "early_stopping"

    def test_early_stopping_custom_params(self):
        """Test EarlyStopping with custom parameters."""
        callback = tl.early_stopping(patience=10, min_delta=0.001)
        assert callback.callback_type == "early_stopping"

    def test_model_checkpoint_creation(self):
        """Test creating ModelCheckpoint callback."""
        callback = tl.model_checkpoint()
        assert callback.callback_type == "model_checkpoint"

    def test_logger_creation(self):
        """Test creating Logger callback."""
        callback = tl.logger()
        assert callback.callback_type == "logger"

    def test_logger_verbose_levels(self):
        """Test logger with different verbose levels."""
        callback_silent = tl.logger(verbose=0)
        callback_progress = tl.logger(verbose=1)
        callback_detailed = tl.logger(verbose=2)

        assert callback_silent.callback_type == "logger"
        assert callback_progress.callback_type == "logger"
        assert callback_detailed.callback_type == "logger"

    def test_callback_repr(self):
        """Test callback string representation."""
        callback = tl.early_stopping()
        repr_str = repr(callback)
        assert "Callback" in repr_str


class TestTrainingHistory:
    """Tests for TrainingHistory."""

    def test_history_creation(self):
        """Test creating training history."""
        history = tl.TrainingHistory()
        assert history.num_epochs() == 0

    def test_add_train_loss(self):
        """Test adding training loss."""
        history = tl.TrainingHistory()
        history.add_train_loss(0.5)
        history.add_train_loss(0.4)

        assert len(history.train_losses) == 2
        assert abs(history.train_losses[0] - 0.5) < 1e-9
        assert abs(history.train_losses[1] - 0.4) < 1e-9

    def test_add_val_loss(self):
        """Test adding validation loss."""
        history = tl.TrainingHistory()
        history.add_val_loss(0.6)
        history.add_val_loss(0.5)

        assert len(history.val_losses) == 2

    def test_add_metric(self):
        """Test adding custom metrics."""
        history = tl.TrainingHistory()
        history.add_metric("accuracy", 0.85)
        history.add_metric("accuracy", 0.90)

        metric_values = history.get_metric("accuracy")
        assert len(metric_values) == 2
        assert abs(metric_values[0] - 0.85) < 1e-9
        assert abs(metric_values[1] - 0.90) < 1e-9

    def test_num_epochs(self):
        """Test getting number of epochs."""
        history = tl.TrainingHistory()
        assert history.num_epochs() == 0

        history.add_train_loss(0.5)
        history.add_train_loss(0.4)
        assert history.num_epochs() == 2

    def test_best_train_loss(self):
        """Test getting best training loss."""
        history = tl.TrainingHistory()
        history.add_train_loss(0.5)
        history.add_train_loss(0.3)
        history.add_train_loss(0.4)

        best_epoch, best_loss = history.best_train_loss()
        assert best_epoch == 1  # Second epoch (0-indexed)
        assert abs(best_loss - 0.3) < 1e-9

    def test_best_val_loss(self):
        """Test getting best validation loss."""
        history = tl.TrainingHistory()
        history.add_val_loss(0.6)
        history.add_val_loss(0.4)
        history.add_val_loss(0.5)

        best_epoch, best_loss = history.best_val_loss()
        assert best_epoch == 1
        assert abs(best_loss - 0.4) < 1e-9

    def test_history_repr(self):
        """Test history string representation."""
        history = tl.TrainingHistory()
        history.add_train_loss(0.5)
        repr_str = repr(history)
        assert "TrainingHistory" in repr_str


class TestTrainer:
    """Tests for Trainer class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a simple expression for testing
        self.expr = tl.pred("x", [tl.var("i"), tl.var("j")])
        self.graph = tl.compile(self.expr)
        self.loss_fn = tl.mse_loss()
        self.optimizer = tl.adam(learning_rate=0.01)

    def test_trainer_creation(self):
        """Test creating a trainer."""
        trainer = tl.Trainer(self.graph, self.loss_fn, self.optimizer)
        assert trainer is not None

    def test_trainer_with_callbacks(self):
        """Test creating trainer with callbacks."""
        callbacks = [tl.early_stopping(), tl.logger()]
        trainer = tl.Trainer(self.graph, self.loss_fn, self.optimizer, callbacks=callbacks)
        assert trainer is not None

    def test_trainer_repr(self):
        """Test trainer string representation."""
        trainer = tl.Trainer(self.graph, self.loss_fn, self.optimizer)
        repr_str = repr(trainer)
        assert "Trainer" in repr_str


class TestTrainingIntegration:
    """Integration tests for full training workflows."""

    def test_simple_training_loop(self):
        """Test a simple training loop."""
        # Create a simple predicate
        expr = tl.pred("x", [tl.var("i"), tl.var("j")])
        graph = tl.compile(expr)

        # Create training data
        train_inputs = {"x": np.random.rand(5, 5)}
        train_targets = np.random.rand(5, 5)

        # Create trainer
        trainer = tl.Trainer(graph, tl.mse_loss(), tl.adam())

        # Train for a few epochs (note: actual optimization not implemented yet)
        # This test mainly verifies the API structure works
        history = trainer.fit(train_inputs, train_targets, epochs=2, verbose=0)

        assert history.num_epochs() <= 2
        assert len(history.train_losses) <= 2


class TestConvenienceFunctions:
    """Tests for convenience training functions."""

    def test_fit_function(self):
        """Test the convenience fit() function."""
        # Create expression
        expr = tl.pred("x", [tl.var("i"), tl.var("j")])

        # Create training data
        train_inputs = {"x": np.random.rand(5, 5)}
        train_targets = np.random.rand(5, 5)

        # Use convenience fit() function
        graph, history = tl.fit(
            expr,
            train_inputs,
            train_targets,
            epochs=2
        )

        assert graph is not None
        assert history.num_epochs() <= 2

    def test_fit_with_custom_loss(self):
        """Test fit() with custom loss function."""
        expr = tl.pred("x", [tl.var("i"), tl.var("j")])
        train_inputs = {"x": np.random.rand(3, 3)}
        train_targets = np.random.rand(3, 3)

        graph, history = tl.fit(
            expr,
            train_inputs,
            train_targets,
            loss_fn=tl.mse_loss(),
            epochs=2
        )

        assert graph is not None
        assert history.num_epochs() <= 2

    def test_fit_with_custom_optimizer(self):
        """Test fit() with custom optimizer."""
        expr = tl.pred("x", [tl.var("i"), tl.var("j")])
        train_inputs = {"x": np.random.rand(3, 3)}
        train_targets = np.random.rand(3, 3)

        graph, history = tl.fit(
            expr,
            train_inputs,
            train_targets,
            optimizer=tl.sgd(learning_rate=0.01),
            epochs=2
        )

        assert graph is not None
        assert history.num_epochs() <= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

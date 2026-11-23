"""Small regression check for soft EM with anchored class identities."""
import numpy as np
from wp5_latent_noise_em.latent_noise_em import LatentNoiseEM


def test_recovers_noise_on_separated_classes():
    rng = np.random.default_rng(7)
    y = np.tile(np.arange(3), 800)
    x = np.eye(3)[y] + rng.normal(0, 0.05, (len(y), 3))
    truth = np.array([[0.75, 0.25, 0], [0, 0.8, 0.2], [0.1, 0, 0.9]])
    observed = np.array([rng.choice(3, p=truth[k]) for k in y[300:]])
    model = LatentNoiseEM(n_classes=3).fit(x[:300], y[:300], x[300:], observed)
    np.testing.assert_allclose(model.get_confusion_matrix().sum(axis=1), 1)
    np.testing.assert_allclose(model.get_confusion_matrix(), truth, atol=0.06)
    assert np.mean(model.predict(x) == y) > 0.99

import numpy as np
from scipy.optimize import curve_fit
from ..settings.const import Const
from ..logs.log import Log


def gaussian(x, a, mu, sigma, offset):
    #sigma = fwhm / 2.3548 if we wanted fhwm instead of sigma as parameter
    if sigma == 0.:
        return 0.
    return a * np.exp(-((x - mu) / sigma)**2 / 2.) + offset


def get_gaussian_fit(abscissa, ordinate, offset_b_min, offset_b_max, q_label=None):
    """
        abscissa and ordinate must be numpy arrays
        
        Returns fit_(used)_bounds, params, y_values
        params is a list of length 3, these are a, mu, sigma as defined in the gaussian function above
    """
    try:
        I_max = max(ordinate)
        #mean = np.average(abscissa, weights=ordinate)  # not really working
        lambda_max = abscissa[ordinate.argmax()]  # lambda that matches I_max
        if q_label is not None:  # not fit maps
            q_label.setText('K bounds: [' + str(offset_b_min) + ', ' + str(offset_b_max) + ']')
        fit_bounds = ([I_max * Const.fit_pc_min, lambda_max * Const.fit_pc_min, Const.sigma_bound_1, offset_b_min],
                      [I_max * Const.fit_pc_max, lambda_max * Const.fit_pc_max, Const.sigma_bound_2, offset_b_max])
        offset_hint = (offset_b_min + offset_b_max) / 2
        fit_hints = [I_max, lambda_max, Const.sigma_hint, offset_hint]
        if I_max > 0:
            params, pcov = curve_fit(gaussian, abscissa, ordinate, p0=fit_hints, bounds=fit_bounds)
            fit_ordinates = gaussian(abscissa, params[0], params[1], params[2], params[3])
        else:
            params = np.array([0., 0., 0., 0.])
            fit_ordinates = [0.] * len(abscissa)
        return fit_bounds, params, fit_ordinates
    except:  # RuntimeError fit not found
        return np.array([]), np.array([0., 0., 0.]), np.array([])


def fit_params_to_str(params, chi2):
    nb_digits = Const.fit_nb_digits
    if isinstance(params[0], list):  # bounds: [params_min, params_max]
        return 'I<sub>max</sub> = ' + str(round(params[0][0], nb_digits)) + '-' + \
            str(round(params[1][0], nb_digits)) + '<br />' + Const.lambda_char + \
            '<sub>max</sub> = ' + str(round(params[0][1], nb_digits)) + '-' + \
            str(round(params[1][1], nb_digits)) + ', ' + Const.sigma_char + ' = ' + \
            str(round(params[0][2], nb_digits)) + '-' + str(round(params[1][2], nb_digits)) + \
            ', K = ' + str(round(params[0][3], nb_digits)) + '-' + str(round(params[1][3], nb_digits))
    else:
        return 'I<sub>max</sub> = ' + str(round(params[0], nb_digits)) + ', ' + Const.lambda_char + \
            '<sub>max</sub> = ' + str(round(params[1], nb_digits)) + ',<br />' + Const.sigma_char + ' = ' + \
            str(round(params[2], nb_digits)) + ', K = ' + str(round(params[3], nb_digits)) + \
            ', Ꭓ<sup>2</sup> = ' + str(chi2)

from flask import Flask, render_template, request, url_for, session
import numpy as np
import matplotlib
from scipy.stats import t

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Replace with your own secret key, needed for session management


def generate_data(N, mu, beta0, beta1, sigma2, S):
    # Generate data and initial plots

    # TODO 1: Generate a random dataset X of size N with values between 0 and 1
    X = np.random.rand(N)  # Generating X dataset with values between 0 and 1



    # TODO 2: Generate a random dataset Y using the specified beta0, beta1, mu, and sigma2
    # Y = beta0 + beta1 * X + mu + error term
    error = np.random.normal(0, np.sqrt(sigma2), N)
    Y = beta0 + beta1 * X + mu + error  # Generating Y dataset based on specified parameters

    # TODO 3: Fit a linear regression model to X and Y
    model = LinearRegression()
    model.fit(X.reshape(-1, 1), Y)
    slope = model.coef_[0]
    intercept = model.intercept_

    # TODO 4: Generate a scatter plot of (X, Y) with the fitted regression line
    plot1_path = "static/plot1.png"
    plt.figure()
    plt.scatter(X, Y, label="Data")
    plt.plot(X, model.predict(X.reshape(-1, 1)), color="red", label="Fit")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Scatter plot of generated data with regression line")
    plt.legend()
    plt.savefig(plot1_path)
    plt.close()

    # TODO 5: Run S simulations to generate slopes and intercepts
    slopes = []
    intercepts = []

    for _ in range(S):
        # TODO 6: Generate simulated datasets using the same beta0 and beta1
        X_sim = np.random.rand(N)
        error_sim = np.random.normal(0, np.sqrt(sigma2), N)
        Y_sim = beta0 + beta1 * X_sim + mu + error_sim

        # TODO 7: Fit linear regression to simulated data and store slope and intercept
        # Fit linear regression to simulated data
        sim_model = LinearRegression()
        sim_model.fit(X_sim.reshape(-1, 1), Y_sim)

        # Extract slope and intercept from the simulated model
        sim_slope = sim_model.coef_[0]
        sim_intercept = sim_model.intercept_

        slopes.append(sim_slope)
        intercepts.append(sim_intercept)

    # TODO 8: Plot histograms of slopes and intercepts
    plot2_path = "static/plot2.png"
    # Create subplots for slope and intercept histograms
    plt.figure(figsize=(12, 5))

    # Histogram for slopes
    plt.subplot(1, 2, 1)
    plt.hist(slopes, bins=30, color='blue', alpha=0.7, label="Simulated Slopes")
    plt.axvline(slope, color='red', linestyle='dashed', linewidth=2, label="Observed Slope")
    plt.xlabel("Slope")
    plt.ylabel("Frequency")
    plt.title("Histogram of Simulated Slopes")
    plt.legend()

    # Histogram for intercepts
    plt.subplot(1, 2, 2)
    plt.hist(intercepts, bins=30, color='green', alpha=0.7, label="Simulated Intercepts")
    plt.axvline(intercept, color='red', linestyle='dashed', linewidth=2, label="Observed Intercept")
    plt.xlabel("Intercept")
    plt.ylabel("Frequency")
    plt.title("Histogram of Simulated Intercepts")
    plt.legend()

    # Save and close the figure
    plt.suptitle("Histograms of Simulated Slopes and Intercepts with Observed Values")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to fit the title
    plt.savefig(plot2_path)
    plt.close()

    # TODO 9: Return data needed for further analysis, including slopes and intercepts
    # Calculate proportions of slopes and intercepts more extreme than observed
    slope_more_extreme = sum([abs(sim_slope) >= abs(slope) for sim_slope in slopes]) / len(slopes)
    intercept_extreme = sum([abs(sim_intercept) >= abs(intercept) for sim_intercept in intercepts]) / len(intercepts)

    # Return data needed for further analysis
    return (
        X,
        Y,
        slope,
        intercept,
        plot1_path,
        plot2_path,
        slope_more_extreme,
        intercept_extreme,
        slopes,
        intercepts,
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get user input from the form
        N = int(request.form["N"])
        mu = float(request.form["mu"])
        sigma2 = float(request.form["sigma2"])
        beta0 = float(request.form["beta0"])
        beta1 = float(request.form["beta1"])
        S = int(request.form["S"])

        # Generate data and initial plots
        (
            X,
            Y,
            slope,
            intercept,
            plot1,
            plot2,
            slope_extreme,
            intercept_extreme,
            slopes,
            intercepts,
        ) = generate_data(N, mu, beta0, beta1, sigma2, S)

        # Store data in session
        session["X"] = X.tolist()
        session["Y"] = Y.tolist()
        session["slope"] = slope
        session["intercept"] = intercept
        session["slopes"] = slopes
        session["intercepts"] = intercepts
        session["slope_extreme"] = slope_extreme
        session["intercept_extreme"] = intercept_extreme
        session["N"] = N
        session["mu"] = mu
        session["sigma2"] = sigma2
        session["beta0"] = beta0
        session["beta1"] = beta1
        session["S"] = S

        # Return render_template with variables
        return render_template(
            "index.html",
            plot1=plot1,
            plot2=plot2,
            slope_extreme=slope_extreme,
            intercept_extreme=intercept_extreme,
            N=N,
            mu=mu,
            sigma2=sigma2,
            beta0=beta0,
            beta1=beta1,
            S=S,
        )
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    # This route handles data generation (same as above)
    return index()


@app.route("/hypothesis_test", methods=["POST"])
def hypothesis_test():
    # Retrieve data from session
    N = int(session.get("N"))
    S = int(session.get("S"))
    slope = float(session.get("slope"))
    intercept = float(session.get("intercept"))
    slopes = session.get("slopes")
    intercepts = session.get("intercepts")
    beta0 = float(session.get("beta0"))
    beta1 = float(session.get("beta1"))

    parameter = request.form.get("parameter")
    test_type = request.form.get("test_type")

    # Use the slopes or intercepts from the simulations
    if parameter == "slope":
        simulated_stats = np.array(slopes)
        observed_stat = slope
        hypothesized_value = beta1
    else:
        simulated_stats = np.array(intercepts)
        observed_stat = intercept
        hypothesized_value = beta0

    # Initialize p_value
    p_value = None

    # Calculate p-value based on test type
    try:
        if test_type == ">":
            p_value = sum(simulated_stats >= observed_stat) / len(simulated_stats)
        elif test_type == "<":
            p_value = sum(simulated_stats <= observed_stat) / len(simulated_stats)
        else:  # Not equal
            p_value = sum(abs(simulated_stats - hypothesized_value) >= abs(observed_stat - hypothesized_value)) / len(simulated_stats)
    except ZeroDivisionError:
        p_value = "N/A"  # Set to a default value if calculation fails

    # Fun message for very small p-value
    fun_message = "Wow! You've encountered a rare event!" if isinstance(p_value, float) and p_value <= 0.0001 else None

    # Plot histogram of simulated statistics
    plot3_path = "static/plot3.png"
    plt.figure(figsize=(8, 6))

    # Plot histogram of simulated statistics
    plt.hist(simulated_stats, bins=15, color="skyblue", alpha=0.7, label="Simulated Statistics")

    # Plot the hypothesized value (H0) as a vertical blue line
    plt.axvline(hypothesized_value, color="blue", linestyle="--", linewidth=2,
                label=f"Hypothesized {parameter.capitalize()} (H₀): {hypothesized_value}")

    # Plot the observed statistic as a red dashed line
    plt.axvline(observed_stat, color="red", linestyle="dashed", linewidth=2,
                label=f"Observed {parameter.capitalize()}: {observed_stat:.4f}")

    # Add p-value text at the top of the plot, centered horizontally
    plt.text(0.5, 0.95, f"p-value: {p_value:.4f}", transform=plt.gca().transAxes, ha='center', fontsize=12,
             color="black")

    # Labeling and title
    plt.xlabel(parameter.capitalize())
    plt.ylabel("Frequency")
    plt.title(f"Hypothesis Test for {parameter.capitalize()}")
    plt.legend()

    # Save and close the plot
    plt.savefig(plot3_path)
    plt.close()

    # Return results to template
    return render_template(
        "index.html",
        plot1="static/plot1.png",
        plot2="static/plot2.png",
        plot3=plot3_path,
        parameter=parameter,
        observed_stat=observed_stat,
        hypothesized_value=hypothesized_value,
        N=N,
        beta0=beta0,
        beta1=beta1,
        S=S,
        p_value=p_value,  # Ensure p_value is defined as a valid value
        fun_message=fun_message,
    )


@app.route("/confidence_interval", methods=["POST"])
def confidence_interval():
    # Retrieve data from session
    N = int(session.get("N"))
    mu = float(session.get("mu"))
    sigma2 = float(session.get("sigma2"))
    beta0 = float(session.get("beta0"))
    beta1 = float(session.get("beta1"))
    S = int(session.get("S"))
    X = np.array(session.get("X"))
    Y = np.array(session.get("Y"))
    slope = float(session.get("slope"))
    intercept = float(session.get("intercept"))
    slopes = session.get("slopes")
    intercepts = session.get("intercepts")

    parameter = request.form.get("parameter")
    confidence_level_str = request.form.get("confidence_level")
    confidence_level = float(confidence_level_str.strip('%'))

    # Use the slopes or intercepts from the simulations
    if parameter == "slope":
        estimates = np.array(slopes)
        observed_stat = slope
        true_param = beta1
    else:
        estimates = np.array(intercepts)
        observed_stat = intercept
        true_param = beta0

    # TODO 14: Calculate mean and standard deviation of the estimates
    mean_estimate = np.mean(estimates)
    std_error = np.std(estimates, ddof=1) / np.sqrt(len(estimates))

    # TODO 15: Calculate confidence interval for the parameter estimate
    # Use the t-distribution and confidence_level
    alpha = 1 - confidence_level / 100
    t_critical = t.ppf(1 - alpha / 2, df=len(estimates) - 1)

    # Calculate the percentiles as required for the confidence interval
    ci_lower = mean_estimate - t_critical * std_error
    ci_upper = mean_estimate + t_critical * std_error

    # TODO 16: Check if confidence interval includes true parameter
    includes_true = ci_lower <= true_param <= ci_upper

    # TODO 17: Plot the individual estimates as gray points and confidence interval
    # Plot the mean estimate as a colored point which changes if the true parameter is included
    # Plot the confidence interval as a horizontal line
    # Plot the true parameter value
    # Plot the confidence interval for the estimates
    plot4_path = "static/plot4.png"
    plt.figure(figsize=(8, 6))

    # Scatter plot for simulated estimates
    plt.scatter(estimates, np.zeros_like(estimates), color="gray", alpha=0.6, label="Simulated Estimates")

    # Plot the mean estimate as a blue point
    plt.plot([mean_estimate], [0], 'o', color="blue", label="Mean Estimate", markersize=10)

    # Plot the confidence interval as a horizontal line
    plt.hlines(0, ci_lower, ci_upper, color="blue", linestyle="-", linewidth=2,
               label=f"{confidence_level}% Confidence Interval")

    # Plot the true parameter as a green dashed line
    plt.axvline(true_param, color="green", linestyle="--", linewidth=2, label="True Parameter")

    # Adjust x-axis limits to give a clearer view
    plt.xlim(min(ci_lower - 0.1, min(estimates) - 0.1), max(ci_upper + 0.1, max(estimates) + 0.1))

    # Labeling and legend
    plt.xlabel(f"{parameter.capitalize()} Estimate")
    plt.title(f"{confidence_level}% Confidence Interval for {parameter.capitalize()} (Mean Estimate)")
    plt.legend()
    plt.grid(True)
    plt.savefig(plot4_path)
    plt.close()
    # Return results to template
    return render_template(
        "index.html",
        plot1="static/plot1.png",
        plot2="static/plot2.png",
        plot4=plot4_path,
        parameter=parameter,
        confidence_level=confidence_level,
        mean_estimate=mean_estimate,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        includes_true=includes_true,
        observed_stat=observed_stat,
        N=N,
        mu=mu,
        sigma2=sigma2,
        beta0=beta0,
        beta1=beta1,
        S=S,
    )


if __name__ == "__main__":
    app.run(debug=True)

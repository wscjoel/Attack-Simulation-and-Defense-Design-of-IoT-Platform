# Security Privacy Coursework - Group 4

This repository contains code for simulating various security attacks on a mock IoT device management web application, as well as implementations of defense strategies.

## Repository Structure

- `Local server html/`: HTML files for running the local mock IoT device management site.
- `DDoS/`: Scripts to simulate distributed denial-of-service attacks.
- `brute force/` and `brute-force/`: Scripts to simulate brute-force attacks. Refer to each folder's README for details.
- `phishing-demo/`: Demonstration scripts for phishing attack simulations.
- `XSS/`: Cross-site scripting attack simulations.
- `MITM/`: Man-in-the-middle attack simulations.
- `Defense_strategy_implementation/`: Code implementing various defense strategies.
  - `security_defenses_implementation.py`: Main implementation of defense mechanisms.
  - `test_security_defenses.py`: Unit tests for the defense implementations.
- `Simulation Presentation/`: Presentation slides and materials for the simulation project.

## Prerequisites

- Python 3.7 or higher
- `pip` package manager

## Setup

1. Clone the repository.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Simulations

Navigate to the respective folder and follow its README instructions. For example:
```bash
cd DDoS
python ddos_attack.py
```

## Running Defense Implementations

```bash
python security_defenses_implementation.py
```


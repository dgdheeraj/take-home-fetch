# Fetch Take-Home Exercise — Site Reliability Engineering

Take-Home Exercise for Fetch Site Reliability Engineering based on the [specifications](https://fetch-hiring.s3.us-east-1.amazonaws.com/site-reliability-engineer/health-check.pdf)
The script checks the health of a set of HTTP endpoints every 15s and displays the availability for every domain.

## Steps to Run
1. Clone the repository
```bash
git  clone  https://github.com/dgdheeraj/take-home-fetch.git
```
2.  Go to the cloned repository
```bash
cd take-home-fetch
```
3.  Create and start the virtual environment (optional)
```bash
python -m venv myenv
```
```bash
# Windows  
myenv\Scripts\activate  
```
```bash
# macOS and Linux  
source myenv/bin/activate
```
4.  Install required modules
```bash
pip install -r requirements.txt
```
5. Run the Health Check script to test the endpoints
```bash
python run_health_check.py test_input.yaml
```
import requests
import time
import json
from datetime import date
import os

class APITesting:
    # Initialize with API client, endpoint, and authentication details
    def __init__(self, api_client, api_endpoint, api_key):
        self.api_client = api_client
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.url = self.correct_url()

    # Just in case the URL is malformed
    def correct_url(self, endpoint=None) -> str:
        if not endpoint:
            endpoint = self.api_endpoint

        if (self.api_client.endswith('/') and endpoint.startswith('/')):
            return self.api_client[:-1] + endpoint
        elif (not self.api_client.endswith('/') and not endpoint.startswith('/')):
            return self.api_client + '/' + endpoint
        else:
            return self.api_client + endpoint

    # Send a GET request to the API endpoint
    def send_get_request(self, session, url, params=None):
        if self.api_key == "":
            headers = None
        else:
            headers = {'Authorization': f'Token {self.api_key}'}

        if session:
            response = session.get(url, params=params, headers=headers)
        else:
            response = requests.get(url, params=params, headers=headers)
        return response
    
    # Calculate the response time of the API endpoint
    def response_time_test(self, url, frequency=20, method='GET', params=None) -> dict:
        msgs = []
        times = []

        if (frequency < 10):
            frequency = 10
            print("Frequency given was below the required threshold of 10. Setting frequency to 10.")

        # Initialize session for handshake minimization
        with requests.Session() as session:

            # Warm-up request
            test_t0 = time.perf_counter()
            res = self.send_get_request(session, url, params=params)
            test_t1 = time.perf_counter()

            response_time = (test_t1 - test_t0) * 1000  # Convert to milliseconds

            if res.status_code != 200:
                raise Exception(f"API request failed with status code {res.status_code}: {res.reason}")
            
            if (response_time < 100):
                # If response time is less than 100ms, do bulk requests to get more accurate average
                t0 = time.perf_counter()
                for _ in range(frequency):
                    res = self.send_get_request(session, url, params=params)
                    msgs.append(f"{res.status_code} : {res.reason}")
                t1 = time.perf_counter()
                total_time = (t1 - t0) * 1000  # Convert to milliseconds
                avg_response_time = total_time / frequency
                return {
                    "avg_response_time_ms": avg_response_time,
                    "total_requests": frequency,
                    "total_time_ms": total_time,
                    "messages": msgs,
                    "individual_response_time_ms": None,
                    "response" : res.json()
                }
            else:
                # Otherwise, measure each request individually
                for _ in range(frequency):
                    t0 = time.perf_counter()
                    res = self.send_get_request(session, url, params=params)
                    t1 = time.perf_counter()
                    msgs.append(f"{res.status_code} : {res.reason}")
                    times.append((t1 - t0) * 1000)  # Convert to milliseconds

                return {
                    "avg_response_time_ms": sum(times) / frequency,
                    "total_requests": frequency,
                    "total_time_ms": sum(times),
                    "messages": msgs,
                    "individual_response_time_ms": times,
                    "response" : res.json()
                }

    # Endpoint response time comparison test between basesline and our target API endpoint
    def ep_comparison_test(self, baseline_endpoint, frequency=20):
        baseline_url = self.correct_url(baseline_endpoint)
        baseline_results = self.response_time_test(baseline_url, frequency=frequency)
        target_results = self.response_time_test(self.url, frequency=frequency)

        return baseline_results, target_results
    
    # Calculate the volume of data in the API response (bytes, number of items, etc.)
    def response_volume_calculator(self, res) -> dict:
        json_bytes = json.dumps(res, ensure_ascii=False, separators=(",", ":")).encode('utf8')
        return {
            "response_size_bytes": len(json_bytes),
            "number_of_items": len(res) if isinstance(res, list) else 1
        }
    
    # Pretty print organizes the displayed data (for console output)
    def pretty_print(self, data) -> None:
        pad = 30
        for k, v in data.items():
            print(f"{k:{pad}} : {v}")

    # Generate a thorough report of the API tests
    def generate_report(self, baseline, frequency=20) -> None:
        today = date.today()
        m = today.month
        d = today.day
        y = today.year

        if not os.path.exists("api_test_reports"):
            os.makedirs("api_test_reports")
            reports = []
        else:
            reports = os.listdir("api_test_reports")
        
        if (f"{y}_{m}_{d}_api_test_report.json" in reports):
            print("Report for today already exists. Please view the existing report to avoid stressing the API endpoint.")
            return

        print("Generating API test report...")

        baseline_result, target_result = self.ep_comparison_test(baseline, frequency=frequency)

        target_volume = self.response_volume_calculator(target_result['response'])
        baseline_volume = self.response_volume_calculator(baseline_result['response'])

        report = {
            "date": f"{y}-{m}-{d}",
            "target_endpoint": self.url,
            "target_avg_rt": target_result["avg_response_time_ms"],
            "target_volume": target_volume,
            "baseline_endpoint": baseline,
            "baseline_avg_rt": baseline_result["avg_response_time_ms"],
            "baseline_volume": baseline_volume,
        }

        self.pretty_print(report)

        report["target_individual_response_times"] = target_result["individual_response_time_ms"]
        report["baseline_individual_response_times"] = baseline_result["individual_response_time_ms"]
        report["target_messages"] = target_result["messages"]
        report["baseline_messages"] = baseline_result["messages"]

        with open(f"api_test_reports/{y}_{m}_{d}_api_test_report.json", "w") as f:
            json.dump(report, f, indent=4)

        with open(f"api_test_reports/{y}_{m}_{d}_target_api_content.txt", "w") as f:
            json.dump(target_result['response'], f, indent=4)
        
        with open(f"api_test_reports/{y}_{m}_{d}_baseline_api_content.txt", "w") as f:
            json.dump(baseline_result['response'], f, indent=4)
        

def main():
    api_client = "https://goadmin.ifrc.org"
    api_endpoint = "/api/v2/dref3"
    api_key = "66a781e9c0b7b800af50461abae48368fa364d1d"
    tester = APITesting(api_client, api_endpoint, api_key)
    
    '''
    Enter your solution here to test the API endpoints.

    Please look at the commented line below for an example of how to generate a report / use the endpoint.
    '''
    # tester.generate_report("/api/v2/appeal", frequency=20)
    

if __name__ == "__main__":
    main()
from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/job_search')
def job_search():
    url = "https://jsearch.p.rapidapi.com/search"
    querystring = {"query": "Web Developer in India", "page": "1", "num_pages": "1"}
    headers = {
        "X-RapidAPI-Key": "78de5d7136msh95cc7d89e509b29p129654jsnf707f12324c1",
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    
    if 'data' in data:
        search_results = data['data']
        results = []
        for result in search_results:
            job_info = {
                "Employer Name": result.get('employer_name', 'N/A'),
                "Job Description": result.get('job_description', 'N/A'),
                "Job Apply Link": result.get('job_apply_link', 'N/A'),
                "Skills required": result.get('job_required_skills', 'N/A')
            }
            results.append(job_info)
        return jsonify(results)
    else:
        error_message = {"error": data.get('error', 'Unknown error')}
        return jsonify(error_message)

if __name__ == '__main__':
    app.run(debug=True)

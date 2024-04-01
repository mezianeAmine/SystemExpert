from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

class UserFacts:
    def __init__(self):
        self.facts = []

    def add_fact(self, fact):
        self.facts.append(fact)

    def remove_fact(self, fact):
        self.facts.remove(fact)

    def clear(self):
        self.facts = []

class DiagnosticSystem:
    def __init__(self):
        self.rule_base = []
        self.user_facts = UserFacts()

    def load_rules(self, file_path):
        with open(file_path, 'r') as f:
            for line in f:
                rule_parts = line.strip().split(":")
                conditions = rule_parts[0].split(",")
                outcome = rule_parts[1]
                self.rule_base.append({'conditions': conditions, 'outcome': outcome})

    def add_user_fact(self, fact):
        self.user_facts.add_fact(fact)

    def clear_user_facts(self):
        self.user_facts.clear()

    def analyze(self):
        issues_detected = set()
        for rule in self.rule_base:
            if set(rule['conditions']).issubset(self.user_facts.facts):
                issues_detected.add(rule['outcome'])
        return issues_detected

system = DiagnosticSystem()

@app.route('/')
def home():
    system.load_rules("base_updated.txt")
    return render_template('index.html', rules=system.rule_base)

@app.route('/diagnose', methods=['POST'])
def diagnose():
    data = request.get_json()
    selected_symptoms = data.get('selected_symptoms')

    if not selected_symptoms:
        return jsonify({'status': 'error', 'message': 'Please select at least one symptom for diagnosis.'})

    symptoms = [system.rule_base[int(index)]['conditions'] for index in selected_symptoms]
    for symptom in symptoms:
        system.add_user_fact(symptom)

    detected_issues = system.analyze()

    message = "Potential issues detected: " + ", ".join(detected_issues) if detected_issues else "System appears to be functioning normally."

    system.clear_user_facts()

    return jsonify({'status': 'success', 'message': message})


if __name__ == '__main__':
    app.run(debug=True)

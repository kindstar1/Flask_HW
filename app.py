from flask import Flask, request, jsonify
from db import Ad, Session

app = Flask(__name__)
app.json.ensure_ascii = False

@app.route('/ads', methods=['POST'])
def create_ad():

    if not request.json:
        return jsonify({"error": "JSON data required"}), 400
    
    data = request.json
    
    if 'title' not in data:
        return jsonify({"error": "title is required"}), 400
    
    if 'owner' not in data:
        return jsonify({"error": "owner is required"}), 400
    
    title = data['title']
    owner = data['owner']
    description = data.get('description', '')
    
    ad = Ad(title=title, description=description, owner=owner)
    
    try:
        with Session() as session:
            session.add(ad)
            session.commit()
            session.refresh(ad)
            return jsonify(ad.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ads/<int:id>', methods=['GET'])
def get_ad(id):
    with Session() as session:
        ad = session.get(Ad, id)
        if ad is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(ad.to_dict()), 200


@app.route('/ads/<int:id>', methods=['DELETE'])
def delete_ad(id):
    with Session() as session:
        ad = session.get(Ad, id)
        if ad is None:
            return jsonify({"error": "not found"}), 404
        session.delete(ad)
        session.commit()
        return jsonify({"message": "ad deleted"}), 200


@app.route('/')
def main():
    return "Server is running"

if __name__ == '__main__':
    app.run(debug=True)

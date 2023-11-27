from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# # Enable CORS with specific origins
# CORS(app, resources={r"/api/*": {"origins": "http://localhost"}})

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'  # Use SQLite as the database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking as it's not needed
db = SQLAlchemy(app)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.String(100), nullable=False)
    suit = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    player = db.relationship('Player', backref=db.backref('cards', lazy=True))

with app.app_context():
    db.create_all()


# Dummy data for testing
with app.app_context():
    existing_player = Player.query.filter_by(name='Jimmy').first()
    if not existing_player:
        player = Player(name='Jimmy')
        db.session.add(player)

        card1 = Card(rank='2',suit='heart',color='red',value=2,player=player)
        card2 = Card(rank='3',suit='spade',color='black',value=3,player=player)
        db.session.add_all([card1,card2])
        db.session.commit()


# Route to retrieve tasks
@app.route('/players', methods=['GET'])
def get_players():
    players = Player.query.all()  # Retrieve all tasks from the database
    
    player_list = []
    for player in players:
        cards = [{
            'id':card.id,
            'rank':card.rank,
            'suit':card.suit,
            'color':card.color,
            'value':card.value
            } for card in player.cards]
        
        player_list.append({
            'id': player.id,
            'name': player.name,
            'card': cards
        })
    print("GET is activating")
    return jsonify({'players': player_list})

# POST endpoint to add a new player and cards
@app.route('/player', methods=['POST'])
def add_player():
    data = request.get_json()

    # Validate the request JSON
    if 'name' not in data or 'cards' not in data:
        return jsonify({'error': 'Invalid request data'}), 400

    # Create a new player
    new_player = Player(name=data['name'])
    db.session.add(new_player)
    db.session.commit()

    # Add cards to the player
    for card_data in data['cards']:
        new_card = Card(rank = card_data['rank'], 
                        suit = card_data['suit'],
                        color = card_data['color'],
                        value = card_data['value'], 
                        player = new_player)
        
        db.session.add(new_card)

    db.session.commit()

    return jsonify({'message': 'Player and cards added successfully'}), 201


@app.route('/')
def hello():
    return 'Hiyo! I am Bnuuy! Round'

if __name__ == '__main__':
    app.run(debug=True)
from marshmallow import Schema, fields

class ChallengeInput(Schema):
    challenge_id = fields.Integer(required=True)
    challenge_title = fields.String(required=True)
    text = fields.String(required=True)

class GetChallenge(Schema):
    challenge_id = fields.Integer(required=True)

# class InputText(Schema):
#     input_text=fields.String(required=True)

from flask_smorest import Blueprint, abort
from schemas import TagSchema, TagAndItemSchema
from flask.views import MethodView
from models import TagModel, StoreModel, ItemTags, ItemModel

from db import db
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("Tags", __name__, description="Operations on tags")


@blp.route("/store/<int:store_id>/tag")
class TagInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        tag = TagModel(store_id=store_id, **tag_data)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e) + str(tag_data) + str(store_id))

        return tag


@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):

    # @blp.arguments()
    @blp.response(201, TagSchema)
    def get(self, item_id, tag_id):
        item = ItemModel.get_or_404(item_id)
        tag = TagModel.get_or_404(tag_id)

        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"error linking tag and item message={e}")
        return tag

    @blp.response(200, TagSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.get_or_404(item_id)
        tag = TagModel.get_or_404(tag_id)

        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"error removing tag and item message={e}")
        return {'message': "item removed from tag ", "item": item, "tag": tag}


@blp.route("/tag/<int:tag_id>")
class Store(MethodView):

    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @blp.response(202, description="deletes a tag if no item is tagged with it.")
    @blp.alt_response(404, description="tag not found")
    @blp.alt_response(400, description="Returns if the tag is assigned to one or more items, the tag is not deleted")
    def delete(self, tag_id):
        tag = StoreModel.query.get_or_404(tag_id)
        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "tag deleted"}
        abort(400, message="Could not delete tag. make sure tag is not associated with any items")

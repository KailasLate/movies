import operator
from functools import reduce
from django.db.models import Q, Prefetch
from movies_app.models import Movies
from movies_app.serializers.movies_serializer import MoviesSerializer
from utility.response import ApiResponse
from movies.permissions import is_access
from django.core.exceptions import PermissionDenied

from utility.utils import MultipleFieldPKModelMixin, CreateRetrieveUpdateViewSet, get_pagination_resp, transform_list
from utility.constants import *

from movies.permissions import is_login
from json import loads, dumps

class MoviesViewSet(MultipleFieldPKModelMixin, CreateRetrieveUpdateViewSet, ApiResponse):
    serializer_class = MoviesSerializer
    permission_classes = [is_access]
    singular_name = 'Movies'

    def get_object(self, pk):
        try:
            return Movies.objects.filter(pk=pk).exclude(status='deleted')[0]
        except:
            return None

    def retrieve(self, request, category_id=None, **kwargs):
        try:
            # capture data
            instance = self.get_object(category_id)
            if instance is None:
                return ApiResponse.response_not_found(self, message=self.singular_name + ' not found')

            # Format response
            resp_dict = self.transform_single(instance)

            # return success
            return ApiResponse.response_ok(self, data=resp_dict)
        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args[0])])

    def list(self, request, *args, **kwargs):
        try:
            where_array = request.query_params
            # capture data
            sort_by = request.query_params.get('sort_by') if request.query_params.get('sort_by') else 'id'

            sort_direction = request.query_params.get('sort_direction') if request.query_params.get(
                'sort_direction') else 'ascending'

            if sort_direction == 'descending':
                sort_by = '-' + sort_by

            search_keyword = request.query_params.get('keyword')
            obj_list = [('status', 'active')]

            if search_keyword:
                obj_list.append((Q(Q(name__icontains=search_keyword) | Q(director__icontains=search_keyword))))

            q_list = [Q(x) for x in obj_list]
            adv_q_list = [Q(y) for y in ads_list]

            queryset = Movies.objects.filter(reduce(operator.and_, q_list)).order_by(sort_by)
            resp_data = get_pagination_resp(queryset, request)
            response_data = transform_list(self, resp_data.get('data'))
            return ApiResponse.response_ok(self, data=response_data, paginator=resp_data.get('paginator'))

        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args)])

    @is_login
    def create(self, request, *args, **kwargs):
        try:
            # capture data
            data = request.data.copy()
            name = data.get('name')
            if not name:
                return ApiResponse.response_bad_request(self, message='Movie name not found.')

            get_category = Movies.objects.filter(name=name, parent__isnull=True, is_deleted=False)
            if get_category:
                return ApiResponse.response_bad_request(self, message='Movie already exists.')

            # serialize and validate data
            serializer = MoviesSerializer(data=data)
            if serializer.is_valid():
                # save the valid data
                serializer.save()
                response_data = serializer.data
                # return success
                return ApiResponse.response_created(self, data=response_data, message=self.singular_name + ' created')

            error_resp = get_serielizer_error(serializer)
            return ApiResponse.response_bad_request(self, message=error_resp)

        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args[0])])

    @is_login
    def partial_update(self, request, *args, **kwargs):
        try:
            # capture data
            data = request.data.copy()
            name = data.get('name')
            get_id = self.kwargs.get('movie_id')

            # process/format on data
            instance = self.get_object(get_id)
            if instance is None:
                return ApiResponse.response_not_found(self, message=self.singular_name + ' not found')

            get_movie = Movies.objects.filter(name=name)
            if get_movie and str(get_movie[0].id) != get_id:
                return ApiResponse.response_bad_request(self, message='Movie already exists.')

            # serialize and validate data
            serializer = MoviesSerializer(instance, data=data, partial=True)
            if serializer.is_valid():
                # update the valid data
                serializer.save()
                response_data = serializer.data

                # return success
                return ApiResponse.response_ok(self, data=response_data, message=self.singular_name + ' updated')

            error_resp = get_serielizer_error(serializer)
            return ApiResponse.response_bad_request(self, message=error_resp)
        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args[0])])

    @is_login
    def delete(self, request, *args, **kwargs):
        try:
            # capture data
            get_id = self.kwargs.get('movie_id')
            instance = self.get_object(get_id)
            if instance is None:
                return ApiResponse.response_not_found(self, message=self.singular_name + ' not found')

            # delete main entry
            instance.status = 'deleted'
            instance.save()
            # return success
            return ApiResponse.response_ok(self, message=self.singular_name + ' deleted')
        except Exception as e:
            return ApiResponse.response_internal_server_error(self, message=[str(e.args[0])])

    def transform_single(self, instance):
        resp_dict = dict()
        resp_dict['id'] = instance.id
        resp_dict['name'] = instance.name
        resp_dict['director'] = instance.director
        resp_dict['genre'] = instance.genre
        resp_dict['status'] = instance.status
        resp_dict['99popularity'] = instance.popularity
        resp_dict['imdb_score'] = instance.imdb_score
        return resp_dict

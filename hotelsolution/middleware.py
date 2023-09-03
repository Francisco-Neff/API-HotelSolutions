from rest_framework import status

class AddCodMiddleware:
    """
    Middleware to add the 'cod' field to the responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        #This verification will not be performed for 5XX error types.
        if not str(response.status_code).startswith('5'):
            if response.data:
                if not 'cod' in response.data.keys():
                    self.__add_cod(response)
            else:
                response.data = {'cod': 1}
                self.__add_cod(response)

        return response

    def __add_cod(self, response):
        if response.exception or not status.is_success(response.status_code):
            response.data['cod'] = 1
        else:
            response.data['cod'] = 0
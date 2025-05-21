# api/views.py
from django.utils.timezone import now, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, Task
from .serializers import UserSerializer, TaskSerializer
from .permissions import IsAdmin, IsManager
from rest_framework.permissions import IsAuthenticated


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def user_list(request):
    if request.method == 'GET':
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Password hashing happens inside serializer
            return Response(UserSerializer(user).data, status=201)
        return Response(serializer.errors, status=400)

        


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def user_detail(request, pk):
    try:
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        return Response(UserSerializer(user).data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=204)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def task_list(request):
    if request.method == 'GET':
        if request.user.role == 'user':
            tasks = Task.objects.filter(assigned_to=request.user)
        else:
            tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if request.user.role in ['admin', 'manager']:
            serializer = TaskSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)  # ✅ Safe fallback
        else:
            return Response({"detail": "Permission denied."}, status=403)  # ✅ Safe fallback


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def task_detail(request, pk):
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response(status=404)

    if request.user.role == 'user' and task.assigned_to != request.user:
        return Response(status=403)

    if request.method == 'GET':
        return Response(TaskSerializer(task).data)

    elif request.method == 'PUT':
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    elif request.method == 'DELETE':
        task.delete()
        return Response(status=204)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManager])
def assign_task(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    data = request.data.copy()
    data['assigned_to'] = user_id
    serializer = TaskSerializer(data=data)
    if serializer.is_valid():
        task = serializer.save()
        return Response(TaskSerializer(task).data, status=201)

    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManager])
def reactivate_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        if user.role != 'user':
            return Response({'error': 'Can only reactivate user role'})
        user.is_active = True
        user.save()
        return Response({'status': 'User reactivated'})
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Or [IsAuthenticated, IsAdmin]
def user_status_list(request):
    active_users = CustomUser.objects.filter(is_active=True)
    inactive_users = CustomUser.objects.filter(is_active=False)

    return Response({
        "active_users": UserSerializer(active_users, many=True).data,
        "inactive_users": UserSerializer(inactive_users, many=True).data
    })
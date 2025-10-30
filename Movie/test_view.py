# views.py
import json
from django.http import JsonResponse
from django.shortcuts import render

from Movie.models import Video, Movie


def progress_view(request):
    return render(request, 'movie/test.html')


def job_status(request, job_id):
    try:
        job = Video.objects.get(id=job_id)
        data = {
            'status': job.status,
            'error': job.error_message,
        }
        data.update(job.json_data)
        return JsonResponse(data)
    except Video.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)


def active_jobs(request):
    jobs = Video.objects.filter(status__in=['queued', 'processing']).order_by('-created_at')
    dict_jobs = []
    for job in jobs:
        data = {
            'id': str(job.id),
            'input_path': job.file.path,
            'status': job.status,
        }
        data.update(job.json_data)
        dict_jobs.append(data)
    return JsonResponse({"jobs": dict_jobs})


def create_job(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            input_path = data.get('input_path')

            if not input_path:
                return JsonResponse({'error': 'Missing input_path'}, status=400)
            movie = Movie.objects.get(uuid="OZF6MpRtqf")
            job = Video.objects.get(
                movie=movie,
                subbed=True,
                has_intro=False
            )
            job.status='queued'
            job.save()
            data = {
                'id': str(job.id),
                'input_path': job.file.path,
                'status': job.status,
            }
            data.update(job.json_data)
            return JsonResponse(data, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print("Exception: {}".format(e))
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

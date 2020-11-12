from unittest import mock

import pytest
from django.urls import reverse

from pythonpro.django_assertions import dj_assert_contains
from pythonpro.pages.views import ImersaoDjangoLessonPage


@pytest.fixture
def client(client, cohort):
    return client


def test_should_return_200_when_load_invite_page(client):
    resp = client.get(reverse('pages:imersao_django_landing_page'))
    assert resp.status_code == 200


@pytest.fixture
def subscribe_with_no_role(mocker):
    return mocker.patch('pythonpro.domain.subscription_domain.subscribe_with_no_role.delay')


# TODO: move this phone tests do generic context
def test_should_call_update_when_with_correct_parameters(subscribe_with_no_role, client):
    client.post(
        reverse('pages:imersao_django_landing_page'),
        {'name': 'Moacir', 'email': 'moacir@python.pro.br'},
        secure=True
    )

    subscribe_with_no_role.assert_called_with(None, 'Moacir', 'moacir@python.pro.br', mock.ANY)


# TODO: move this phone tests do generic context
def test_should_call_update_when_logged_with_correct_parameters(subscribe_with_no_role,
                                                                client_with_user):
    resp_with_user = client_with_user.post(
        reverse('pages:imersao_django_landing_page'),
        {'name': 'Moacir', 'email': 'moacir@python.pro.br'},
        secure=True
    )

    subscribe_with_no_role.assert_called_with(
        resp_with_user.cookies['sessionid'].value,
        'Moacir',
        'moacir@python.pro.br',
        mock.ANY
    )


def test_should_run_form_ok(subscribe_with_no_role, client, cohort):
    resp = client.post(
        reverse('pages:imersao_django_landing_page'),
        {'name': 'Moacir', 'email': 'moacir@python.pro.br'},
        secure=True
    )

    assert resp.status_code == 302


def test_should_inform_form_error(subscribe_with_no_role, client, cohort):
    resp = client.post(
        reverse('pages:imersao_django_landing_page'),
        {'name': 'Moacir', 'email': 'moacirpython.pro.br'},
        secure=True
    )

    assert resp.status_code == 200
    dj_assert_contains(resp, 'is-invalid')


@pytest.mark.parametrize(
    'lesson_number',
    range(1, 8)
)
def test_should_return_200_when_load_lesson_page(client, lesson_number):
    resp = client.get(reverse('pages:imersao_django_lesson_page', args=[lesson_number, ]))
    assert resp.status_code == 200


@pytest.mark.parametrize(
    'lesson_number',
    range(1, 8)
)
def test_should_send_video_id_to_context_data(client, lesson_number):
    resp = client.get(reverse('pages:imersao_django_lesson_page', args=[lesson_number, ]))
    assert resp.context_data['video']['id'] is not None


def test_should_return_404_when_lesson_doesnt_exists(client):
    resp = client.get(reverse('pages:imersao_django_lesson_page', args=[8, ]))
    assert resp.status_code == 404


@pytest.mark.parametrize(
    'lesson_number',
    range(1, 8)
)
def test_should_appear_correct_video_id_in_content(client, lesson_number):
    resp = client.get(reverse('pages:imersao_django_lesson_page', args=[lesson_number, ]))
    video_information = ImersaoDjangoLessonPage.get_video_informations(lesson_number)
    assert video_information['id'] in resp.content.decode()
    assert video_information['title'] in resp.content.decode()


@pytest.mark.parametrize(
    'lesson_number',
    range(1, 7)
)
def test_should_send_next_video_id_to_context_data(client, lesson_number):
    resp = client.get(reverse('pages:imersao_django_lesson_page', args=[lesson_number, ]))
    next_url = reverse('pages:imersao_django_lesson_page', args=[lesson_number + 1, ])
    assert next_url in resp.content.decode()


@pytest.mark.parametrize(
    'lesson_number',
    range(2, 8)
)
def test_should_previous_previous_video_id_to_context_data(client, lesson_number):
    resp = client.get(reverse('pages:imersao_django_lesson_page', args=[lesson_number, ]))
    previous_url = reverse('pages:imersao_django_lesson_page', args=[lesson_number - 1, ])
    assert previous_url in resp.content.decode()

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import AcademicProgramme, LearningResource


DEFAULT_WEIGHTS = {
    'interest': 0.25,
    'academic': 0.25,
    'career': 0.20,
    'qualification': 0.20,
    'study': 0.10,
}


def _normalise_list(value):
    if value is None:
        return set()
    if isinstance(value, (list, tuple, set)):
        items = value
    else:
        items = str(value).split(',')
    cleaned = []
    for item in items:
        if isinstance(item, str):
            item = item.strip().lower()
            if item:
                cleaned.append(item)
        else:
            cleaned.append(str(item).strip().lower())
    return set(cleaned)


def _jaccard_similarity(left, right):
    if not left and not right:
        return 0.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def _text_similarity(profile_text, candidate_text):
    if not profile_text or not candidate_text:
        return 0.0
    vectorizer = TfidfVectorizer(stop_words='english')
    matrix = vectorizer.fit_transform([profile_text, candidate_text])
    similarity = cosine_similarity(matrix[0], matrix[1])[0][0]
    return float(np.clip(similarity, 0.0, 1.0))


def _build_profile_text(profile):
    if profile is None:
        return ''
    parts = [
        profile.academic_background,
        profile.academic_subjects,
        profile.preferred_fields,
        profile.career_interests,
        profile.academic_goals,
        profile.learning_style,
        profile.study_mode,
        ' '.join(profile.get_interest_names()),
    ]
    return ' '.join(part for part in parts if part and str(part).strip())


def _build_programme_text(programme):
    parts = [
        programme.name,
        programme.institution,
        programme.faculty,
        programme.academic_field,
        programme.description,
        programme.required_qualifications,
        programme.required_subjects,
        programme.career_opportunities,
        programme.skills_associated,
        programme.interest_tags,
    ]
    return ' '.join(part for part in parts if part and str(part).strip())


def _build_resource_text(resource):
    parts = [
        resource.title,
        resource.description,
        resource.subject,
        resource.category,
        resource.learning_format,
        resource.skills_covered,
        resource.interest_tags,
    ]
    return ' '.join(part for part in parts if part and str(part).strip())


def _qualification_score(profile, programme):
    if not profile or not programme:
        return 0.5
    if not profile.highest_qualification and not programme.required_qualifications:
        return 0.5
    profile_q = profile.highest_qualification.lower()
    req_text = str(programme.required_qualifications or '').lower()
    if not req_text:
        return 0.5
    if 'secondary' in profile_q and 'secondary' in req_text:
        return 1.0
    if 'diploma' in profile_q and ('diploma' in req_text or 'certificate' in req_text or 'secondary' in req_text):
        return 0.9
    if 'undergraduate' in profile_q and ('undergraduate' in req_text or 'secondary' in req_text):
        return 0.95
    if 'postgraduate' in profile_q:
        return 0.85
    return 0.6


def _study_score(profile, item):
    if not profile or not item:
        return 0.5
    profile_study = str(profile.study_mode or '').lower()
    item_study = str(getattr(item, 'study_mode', '') or '').lower()
    if not profile_study or not item_study:
        return 0.7
    return 1.0 if profile_study == item_study else 0.5


def generate_programme_recommendations(student_profile, programmes=None, limit=5):
    if student_profile is None:
        return []
    if programmes is None:
        programmes = AcademicProgramme.objects.filter(is_active=True)
    programmes = list(programmes.filter(is_active=True)) if hasattr(programmes, 'filter') else list(programmes)
    if not programmes:
        return []

    profile_interests = _normalise_list(student_profile.get_interest_names())
    profile_subjects = _normalise_list(student_profile.academic_subjects)
    profile_career = _normalise_list(student_profile.career_interests)
    profile_fields = _normalise_list(student_profile.preferred_fields)
    profile_text = _build_profile_text(student_profile)

    recommendations = []
    for programme in programmes:
        programme_interest_tags = _normalise_list(programme.interest_tags)
        programme_subjects = _normalise_list(programme.required_subjects)
        programme_careers = _normalise_list(programme.career_opportunities)
        programme_fields = _normalise_list(programme.academic_field)
        text_similarity = _text_similarity(profile_text, _build_programme_text(programme))

        interest_score = _jaccard_similarity(profile_interests, programme_interest_tags)
        academic_score = _jaccard_similarity(profile_subjects, programme_subjects)
        career_score = _jaccard_similarity(profile_career, programme_careers)
        field_score = _jaccard_similarity(profile_fields, programme_fields)
        qualification_score = _qualification_score(student_profile, programme)
        study_score = _study_score(student_profile, programme)

        final_score = (
            DEFAULT_WEIGHTS['interest'] * interest_score +
            DEFAULT_WEIGHTS['academic'] * max(academic_score, field_score) +
            DEFAULT_WEIGHTS['career'] * career_score +
            DEFAULT_WEIGHTS['qualification'] * qualification_score +
            DEFAULT_WEIGHTS['study'] * study_score +
            (0.15 * text_similarity)
        )

        final_score = max(0.0, min(1.0, final_score)) * 100
        if final_score < 5:
            continue

        matching_factors = []
        if interest_score > 0:
            matching_factors.append('Shared interests')
        if academic_score > 0 or field_score > 0:
            matching_factors.append('Academic alignment')
        if career_score > 0:
            matching_factors.append('Career path fit')
        if qualification_score >= 0.8:
            matching_factors.append('Qualification compatibility')
        if not matching_factors:
            matching_factors.append('Profile fit based on contextual similarity')

        skill_gaps = []
        if programme.skills_associated:
            known_skills = _normalise_list(student_profile.academic_subjects) | _normalise_list(student_profile.academic_goals)
            for skill in _normalise_list(programme.skills_associated):
                if skill not in known_skills and skill not in _normalise_list(student_profile.career_interests):
                    skill_gaps.append(skill.title())
        suggestions = [
            'Review the programme entry and compare it with your academic strengths.',
            'Explore the course structure and career pathways before applying.',
            'If needed, strengthen your relevant subjects or seek mentoring in the programme field.',
        ]

        explanation = (
            f'{programme.name} matches your profile because it aligns with your interest in {", ".join(sorted(profile_interests)[:3] or ["your academic goals"])}, '
            f'and the programme supports pathways such as {", ".join(sorted(programme_careers)[:3] or ["future career growth"]) }.'
        )

        recommendations.append({
            'programme': programme,
            'score': round(final_score, 2),
            'matching_factors': matching_factors,
            'skill_gaps': skill_gaps[:3],
            'suggested_next_steps': suggestions,
            'explanation': explanation,
        })

    recommendations.sort(key=lambda item: item['score'], reverse=True)
    return recommendations[:limit]


def generate_resource_recommendations(student_profile, resources=None, limit=5):
    if student_profile is None:
        return []
    if resources is None:
        resources = LearningResource.objects.filter(is_active=True)
    resources = list(resources.filter(is_active=True)) if hasattr(resources, 'filter') else list(resources)
    if not resources:
        return []

    profile_interests = _normalise_list(student_profile.get_interest_names())
    profile_subjects = _normalise_list(student_profile.academic_subjects)
    profile_career = _normalise_list(student_profile.career_interests)
    profile_text = _build_profile_text(student_profile)

    recommendations = []
    for resource in resources:
        resource_interests = _normalise_list(resource.interest_tags)
        resource_skills = _normalise_list(resource.skills_covered)
        resource_subjects = _normalise_list(resource.subject)
        text_similarity = _text_similarity(profile_text, _build_resource_text(resource))

        interest_score = _jaccard_similarity(profile_interests, resource_interests)
        subject_score = _jaccard_similarity(profile_subjects, resource_subjects)
        skill_score = _jaccard_similarity(profile_career, resource_skills)
        learning_score = 1.0 if str(student_profile.learning_style or '').lower() in str(resource.learning_format or '').lower() else 0.7
        final_score = (0.30 * interest_score) + (0.25 * subject_score) + (0.20 * skill_score) + (0.15 * learning_score) + (0.10 * text_similarity)
        final_score = max(0.0, min(1.0, final_score)) * 100
        if final_score < 5:
            continue

        explanation = (
            f'{resource.title} supports your learning goals by reinforcing skills in {resource.subject} and matching your interest in '
            f'{", ".join(sorted(profile_interests)[:3] or ["academic growth"]) }.'
        )

        recommendations.append({
            'resource': resource,
            'score': round(final_score, 2),
            'matching_factors': ['Interest alignment', 'Subject relevance', 'Learning preference match'],
            'explanation': explanation,
            'suggested_next_steps': [f'Review the resource: {resource.title}', 'Apply the concepts to a mini project or practical exercise.'],
        })

    recommendations.sort(key=lambda item: item['score'], reverse=True)
    return recommendations[:limit]


def get_recommendation_summary(student_profile):
    if student_profile is None:
        return {'status': 'incomplete', 'message': 'No profile available.'}
    profile_text = _build_profile_text(student_profile)
    programmes = list(AcademicProgramme.objects.filter(is_active=True))
    resources = list(LearningResource.objects.filter(is_active=True))
    is_complete = bool(profile_text and (student_profile.career_interests or student_profile.preferred_fields or student_profile.academic_subjects))
    return {
        'status': 'ready' if is_complete else 'incomplete',
        'programme_count': len(programmes),
        'resource_count': len(resources),
        'message': 'Profile is complete and recommendations can be generated.' if is_complete else 'Profile information is incomplete; recommendations may be less specific.',
    }

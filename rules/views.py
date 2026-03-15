from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import RuleSet, Rule


def ruleset_list(request):
    rulesets = RuleSet.objects.prefetch_related('rules').all()
    return render(request, 'rules/ruleset_list.html', {'rulesets': rulesets})


def ruleset_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Ruleset name is required.')
            return render(request, 'rules/ruleset_form.html', {'action': 'Create'})
        ruleset = RuleSet.objects.create(
            name=name,
            description=request.POST.get('description', ''),
            is_default=request.POST.get('is_default') == 'on',
        )
        messages.success(request, f'Ruleset "{ruleset.name}" created.')
        return redirect('rules:ruleset_detail', pk=ruleset.pk)
    return render(request, 'rules/ruleset_form.html', {'action': 'Create'})


def ruleset_detail(request, pk):
    ruleset = get_object_or_404(RuleSet, pk=pk)
    rules = ruleset.rules.all()
    return render(request, 'rules/ruleset_detail.html', {
        'ruleset': ruleset,
        'rules': rules,
        'rule_types': Rule.RULE_TYPES,
        'severity_choices': Rule.SEVERITY_CHOICES,
    })


def ruleset_edit(request, pk):
    ruleset = get_object_or_404(RuleSet, pk=pk)
    if request.method == 'POST':
        ruleset.name = request.POST.get('name', '').strip()
        ruleset.description = request.POST.get('description', '')
        ruleset.is_default = request.POST.get('is_default') == 'on'
        ruleset.save()
        messages.success(request, 'Ruleset updated.')
        return redirect('rules:ruleset_detail', pk=ruleset.pk)
    return render(request, 'rules/ruleset_form.html', {'ruleset': ruleset, 'action': 'Edit'})


def ruleset_delete(request, pk):
    ruleset = get_object_or_404(RuleSet, pk=pk)
    if request.method == 'POST':
        name = ruleset.name
        ruleset.delete()
        messages.success(request, f'Ruleset "{name}" deleted.')
        return redirect('rules:ruleset_list')
    return render(request, 'rules/ruleset_confirm_delete.html', {'ruleset': ruleset})


def rule_create(request, ruleset_pk):
    ruleset = get_object_or_404(RuleSet, pk=ruleset_pk)
    if request.method == 'POST':
        try:
            rule = Rule.objects.create(
                ruleset=ruleset,
                name=request.POST['name'],
                rule_type=request.POST['rule_type'],
                threshold=float(request.POST['threshold']),
                severity=request.POST.get('severity', 'warning'),
                is_enabled=request.POST.get('is_enabled') == 'on',
                description=request.POST.get('description', ''),
            )
            messages.success(request, f'Rule "{rule.name}" added.')
        except Exception as e:
            messages.error(request, f'Error creating rule: {e}')
        return redirect('rules:ruleset_detail', pk=ruleset_pk)
    return render(request, 'rules/rule_form.html', {
        'ruleset': ruleset,
        'rule_types': Rule.RULE_TYPES,
        'severity_choices': Rule.SEVERITY_CHOICES,
        'action': 'Add',
    })


def rule_edit(request, pk):
    rule = get_object_or_404(Rule, pk=pk)
    ruleset = rule.ruleset
    if request.method == 'POST':
        try:
            rule.name = request.POST['name']
            rule.rule_type = request.POST['rule_type']
            rule.threshold = float(request.POST['threshold'])
            rule.severity = request.POST.get('severity', 'warning')
            rule.is_enabled = request.POST.get('is_enabled') == 'on'
            rule.description = request.POST.get('description', '')
            rule.save()
            messages.success(request, f'Rule "{rule.name}" updated.')
        except Exception as e:
            messages.error(request, f'Error updating rule: {e}')
        return redirect('rules:ruleset_detail', pk=ruleset.pk)
    return render(request, 'rules/rule_form.html', {
        'rule': rule,
        'ruleset': ruleset,
        'rule_types': Rule.RULE_TYPES,
        'severity_choices': Rule.SEVERITY_CHOICES,
        'action': 'Edit',
    })


def rule_delete(request, pk):
    rule = get_object_or_404(Rule, pk=pk)
    ruleset_pk = rule.ruleset.pk
    if request.method == 'POST':
        name = rule.name
        rule.delete()
        messages.success(request, f'Rule "{name}" deleted.')
    return redirect('rules:ruleset_detail', pk=ruleset_pk)


@require_POST
def rule_toggle(request, pk):
    rule = get_object_or_404(Rule, pk=pk)
    rule.is_enabled = not rule.is_enabled
    rule.save()
    return JsonResponse({'enabled': rule.is_enabled})

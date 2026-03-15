from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from network.models import NetworkTopology
from rules.models import RuleSet
from .models import AnalysisResult
from .engine import NetworkAnalyzer


def analysis_list(request):
    results = AnalysisResult.objects.select_related('topology', 'ruleset').all()
    return render(request, 'analysis/analysis_list.html', {'results': results})


def run_analysis(request, topology_pk):
    topology = get_object_or_404(NetworkTopology, pk=topology_pk)
    if request.method == 'POST':
        ruleset_id = request.POST.get('ruleset')
        ruleset = None
        if ruleset_id:
            ruleset = RuleSet.objects.filter(pk=ruleset_id).first()

        analyzer = NetworkAnalyzer(topology, ruleset)
        data = analyzer.run_full_analysis()

        result = AnalysisResult.objects.create(
            topology=topology,
            ruleset=ruleset,
            results_data=data,
            risk_score=data['risk_score'],
            summary=data['summary'],
        )
        messages.success(request, f'Analysis complete. Risk score: {data["risk_score"]:.0f}/100')
        return redirect('analysis:analysis_detail', pk=result.pk)

    rulesets = RuleSet.objects.all()
    return render(request, 'analysis/run_analysis.html', {
        'topology': topology,
        'rulesets': rulesets,
    })


def analysis_detail(request, pk):
    result = get_object_or_404(AnalysisResult, pk=pk)
    data = result.results_data
    return render(request, 'analysis/analysis_detail.html', {
        'result': result,
        'failure_points': data.get('failure_points', {}),
        'routing': data.get('routing', []),
        'suggestions': data.get('device_suggestions', []),
        'violations': data.get('rule_violations', []),
        'stats': data.get('network_stats', {}),
    })


def analysis_delete(request, pk):
    result = get_object_or_404(AnalysisResult, pk=pk)
    topology_pk = result.topology.pk
    if request.method == 'POST':
        result.delete()
        messages.success(request, 'Analysis result deleted.')
        return redirect('network:topology_detail', pk=topology_pk)
    return render(request, 'analysis/analysis_confirm_delete.html', {'result': result})

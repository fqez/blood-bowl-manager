import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:phosphor_flutter/phosphor_flutter.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../roster/domain/models/team.dart';
import '../../../shared/data/repositories.dart';
import '../widgets/race_card.dart';
import '../widgets/position_card.dart';
import '../widgets/budget_bar.dart';

// Provider para obtener los base rosters del backend
final baseRostersProvider = FutureProvider<List<BaseTeam>>((ref) async {
  final repository = ref.watch(teamRepositoryProvider);
  return repository.getBaseTeams();
});

// Provider para obtener el detalle de un roster específico
final baseRosterDetailProvider = FutureProvider.family<BaseTeam, String>((ref, rosterId) async {
  final repository = ref.watch(teamRepositoryProvider);
  return repository.getBaseTeamDetail(rosterId);
});

class TeamCreatorScreen extends ConsumerStatefulWidget {
  final String? leagueId;

  const TeamCreatorScreen({super.key, this.leagueId});

  @override
  ConsumerState<TeamCreatorScreen> createState() => _TeamCreatorScreenState();
}

class _TeamCreatorScreenState extends ConsumerState<TeamCreatorScreen> {
  int _currentStep = 0;

  // Team data
  String _teamName = '';
  BaseTeam? _selectedRace;
  final List<_RecruitedPlayer> _roster = [];
  int _rerolls = 0;
  bool _apothecary = false;
  int _assistantCoaches = 0;
  int _cheerleaders = 0;
  bool _loadingRaceDetail = false;

  static const int _startingBudget = 1000000;

  int get _spent {
    int total = 0;
    for (final player in _roster) {
      total += player.position.cost;
    }
    total += _rerolls * (_selectedRace?.rerollCost ?? 50000);
    if (_apothecary) total += 50000;
    total += _assistantCoaches * 10000;
    total += _cheerleaders * 10000;
    return total;
  }

  int get _remaining => _startingBudget - _spent;

  int get _rosterCount => _roster.length;

  bool get _isValidRoster {
    // At least 11 players
    if (_rosterCount < 11) return false;
    // At least 3 rerolls recommended (soft check)
    return true;
  }

  /// Selecciona una raza y carga su detalle completo desde el backend
  Future<void> _selectRace(BaseTeam raceSummary) async {
    // Si ya está seleccionada y tenemos el detalle, no hacer nada
    if (_selectedRace?.id == raceSummary.id && _selectedRace!.positions.isNotEmpty) {
      return;
    }

    // Mostrar la selección inmediatamente con datos básicos
    setState(() {
      _selectedRace = raceSummary;
      _loadingRaceDetail = true;
      // Limpiar roster si cambiamos de raza
      _roster.clear();
      _rerolls = 0;
    });

    try {
      // Cargar el detalle completo (con posiciones)
      final repository = ref.read(teamRepositoryProvider);
      final detail = await repository.getBaseTeamDetail(raceSummary.id);

      if (mounted) {
        setState(() {
          _selectedRace = detail;
          _loadingRaceDetail = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _loadingRaceDetail = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error al cargar detalles del equipo: $e'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isWide = screenWidth >= 900;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: isWide
          ? null
          : AppBar(
              title: const Text('Crear Equipo'),
              leading: IconButton(
                icon: Icon(PhosphorIcons.arrowLeft(PhosphorIconsStyle.bold)),
                onPressed: () => _showExitDialog(context),
              ),
            ),
      body: isWide ? _buildDesktopLayout() : _buildMobileLayout(),
    );
  }

  Widget _buildDesktopLayout() {
    return Row(
      children: [
        // Sidebar con pasos
        Container(
          width: 260,
          color: AppColors.surface,
          child: Column(
            children: [
              // Header
              Container(
                padding: const EdgeInsets.all(20),
                child: Row(
                  children: [
                    IconButton(
                      icon: Icon(PhosphorIcons.arrowLeft(PhosphorIconsStyle.bold)),
                      onPressed: () => _showExitDialog(context),
                      color: AppColors.textSecondary,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Crear Equipo',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ],
                ),
              ),
              const Divider(height: 1),
              // Steps verticales
              Expanded(child: _buildVerticalSteps()),
              // Budget bar en sidebar
              if (_currentStep > 0)
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: BudgetBar(spent: _spent, total: _startingBudget),
                ),
            ],
          ),
        ),
        // Contenido principal - usa todo el espacio
        Expanded(
          child: Column(
            children: [
              // Header con título del paso actual
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  border: Border(bottom: BorderSide(color: AppColors.surfaceLight)),
                ),
                child: Row(
                  children: [
                    Text(
                      _getStepTitle(),
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    if (_currentStep == 1 && _selectedRace != null) ...[
                      const SizedBox(width: 12),
                      Icon(PhosphorIcons.caretRight(PhosphorIconsStyle.bold),
                          size: 14, color: AppColors.textMuted),
                      const SizedBox(width: 8),
                      Text(
                        _teamName.isNotEmpty ? _teamName : 'Nuevo Equipo',
                        style: TextStyle(
                          fontSize: 14,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                    const Spacer(),
                    _buildDesktopNavigationButtons(),
                  ],
                ),
              ),
              // Contenido scrolleable
              Expanded(
                child: SingleChildScrollView(
                  padding: EdgeInsets.only(
                    left: _currentStep == 1 ? 0 : 32,
                    right: _currentStep == 1 ? 0 : 32,
                    top: _currentStep == 1 ? 0 : 32,
                    bottom: 32,
                  ),
                  child: _buildCurrentStep(true),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  String _getStepTitle() {
    switch (_currentStep) {
      case 0:
        return 'Selecciona una raza';
      case 1:
        return 'Ficha jugadores';
      case 2:
        return 'Personal y equipo';
      case 3:
        return 'Confirmar equipo';
      default:
        return '';
    }
  }

  Widget _buildMobileLayout() {
    return Column(
      children: [
        _buildProgressSteps(),
        if (_currentStep > 0)
          BudgetBar(spent: _spent, total: _startingBudget),
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
            child: _buildCurrentStep(false),
          ),
        ),
        _buildNavigationButtons(),
      ],
    );
  }

  Widget _buildVerticalSteps() {
    final steps = [
      {'title': 'Raza', 'subtitle': 'Selecciona tu equipo'},
      {'title': 'Roster', 'subtitle': 'Ficha jugadores'},
      {'title': 'Personal', 'subtitle': 'Re-rolls y staff'},
      {'title': 'Confirmar', 'subtitle': 'Revisa y crea'},
    ];

    return ListView.builder(
      padding: const EdgeInsets.symmetric(vertical: 16),
      itemCount: steps.length,
      itemBuilder: (context, index) {
        final isActive = index == _currentStep;
        final isCompleted = index < _currentStep;
        final step = steps[index];

        return InkWell(
          onTap: isCompleted ? () => setState(() => _currentStep = index) : null,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
            decoration: BoxDecoration(
              color: isActive ? AppColors.primary.withOpacity(0.1) : null,
              border: Border(
                left: BorderSide(
                  color: isActive
                      ? AppColors.primary
                      : isCompleted
                          ? AppColors.success
                          : Colors.transparent,
                  width: 3,
                ),
              ),
            ),
            child: Row(
              children: [
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    color: isActive
                        ? AppColors.primary
                        : isCompleted
                            ? AppColors.success
                            : AppColors.surfaceLight,
                    shape: BoxShape.circle,
                  ),
                  child: Center(
                    child: isCompleted
                        ? Icon(
                            PhosphorIcons.check(PhosphorIconsStyle.bold),
                            size: 18,
                            color: AppColors.textPrimary,
                          )
                        : Text(
                            '${index + 1}',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                              color: isActive
                                  ? AppColors.textPrimary
                                  : AppColors.textMuted,
                            ),
                          ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        step['title']!,
                        style: TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                          color: isActive || isCompleted
                              ? AppColors.textPrimary
                              : AppColors.textMuted,
                        ),
                      ),
                      Text(
                        step['subtitle']!,
                        style: TextStyle(
                          fontSize: 12,
                          color: AppColors.textMuted,
                        ),
                      ),
                    ],
                  ),
                ),
                if (isCompleted)
                  Icon(
                    PhosphorIcons.caretRight(PhosphorIconsStyle.bold),
                    size: 16,
                    color: AppColors.textMuted,
                  ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildDesktopNavigationButtons() {
    final canProceed = _canProceed();

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (_currentStep > 0) ...[
          OutlinedButton.icon(
            onPressed: () => setState(() => _currentStep--),
            icon: Icon(PhosphorIcons.arrowLeft(PhosphorIconsStyle.bold), size: 16),
            label: const Text('Anterior'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            ),
          ),
          const SizedBox(width: 12),
        ],
        ElevatedButton.icon(
          onPressed: canProceed
              ? () {
                  if (_currentStep < 3) {
                    setState(() => _currentStep++);
                  } else {
                    _createTeam();
                  }
                }
              : null,
          icon: Icon(
            _currentStep < 3
                ? PhosphorIcons.arrowRight(PhosphorIconsStyle.bold)
                : PhosphorIcons.check(PhosphorIconsStyle.bold),
            size: 16,
          ),
          label: Text(_currentStep < 3 ? 'Siguiente' : 'Crear Equipo'),
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          ),
        ),
      ],
    );
  }

  Widget _buildProgressSteps() {
    final steps = ['Raza', 'Roster', 'Personal', 'Confirmar'];

    return Container(
      padding: const EdgeInsets.all(16),
      color: AppColors.surface,
      child: Row(
        children: List.generate(steps.length * 2 - 1, (index) {
          if (index.isOdd) {
            final stepIndex = index ~/ 2;
            return Expanded(
              child: Container(
                height: 2,
                color: stepIndex < _currentStep
                    ? AppColors.primary
                    : AppColors.surfaceLight,
              ),
            );
          } else {
            final stepIndex = index ~/ 2;
            final isActive = stepIndex == _currentStep;
            final isCompleted = stepIndex < _currentStep;

            return Column(
              children: [
                Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    color: isActive
                        ? AppColors.primary
                        : isCompleted
                            ? AppColors.success
                            : AppColors.surfaceLight,
                    shape: BoxShape.circle,
                  ),
                  child: Center(
                    child: isCompleted
                        ? Icon(PhosphorIcons.check(PhosphorIconsStyle.bold),
                            size: 16, color: AppColors.textPrimary)
                        : Text(
                            '${stepIndex + 1}',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                              color: isActive
                                  ? AppColors.textPrimary
                                  : AppColors.textMuted,
                            ),
                          ),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  steps[stepIndex],
                  style: TextStyle(
                    fontSize: 11,
                    color:
                        isActive ? AppColors.textPrimary : AppColors.textMuted,
                  ),
                ),
              ],
            );
          }
        }),
      ),
    );
  }

  Widget _buildCurrentStep(bool isWide) {
    switch (_currentStep) {
      case 0:
        return _buildRaceStep(isWide);
      case 1:
        return _buildRosterStep(isWide);
      case 2:
        return _buildStaffStep(isWide);
      case 3:
        return _buildConfirmStep(isWide);
      default:
        return const SizedBox.shrink();
    }
  }

  Widget _buildRaceStep(bool isWide) {
    final racesAsync = ref.watch(baseRostersProvider);

    return racesAsync.when(
      loading: () => Center(
        child: CircularProgressIndicator(
          color: AppColors.primary,
        ),
      ),
      error: (error, stack) => Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              PhosphorIcons.warning(PhosphorIconsStyle.fill),
              size: 48,
              color: AppColors.error,
            ),
            const SizedBox(height: 16),
            Text(
              'Error al cargar equipos',
              style: TextStyle(color: AppColors.error),
            ),
            const SizedBox(height: 8),
            ElevatedButton(
              onPressed: () => ref.invalidate(baseRostersProvider),
              child: const Text('Reintentar'),
            ),
          ],
        ),
      ),
      data: (races) => _buildRaceStepContent(isWide, races),
    );
  }

  Widget _buildRaceStepContent(bool isWide, List<BaseTeam> races) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Wallpaper del equipo seleccionado
        if (_selectedRace != null) ...[
          Container(
            height: isWide ? 200 : 150,
            width: double.infinity,
            margin: const EdgeInsets.only(bottom: 24),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: AppColors.primary.withOpacity(0.3),
                  blurRadius: 20,
                  offset: const Offset(0, 8),
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Stack(
                fit: StackFit.expand,
                children: [
                  Image.asset(
                    'teams/${_selectedRace!.id}/wallpaper.png',
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => Container(
                      color: AppColors.surfaceLight,
                      child: Center(
                        child: Icon(
                          PhosphorIcons.image(PhosphorIconsStyle.light),
                          size: 48,
                          color: AppColors.textMuted,
                        ),
                      ),
                    ),
                  ),
                  // Gradient overlay
                  Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          Colors.transparent,
                          AppColors.background.withOpacity(0.8),
                        ],
                      ),
                    ),
                  ),
                  // Team name overlay
                  Positioned(
                    bottom: 16,
                    left: 16,
                    right: 16,
                    child: Row(
                      children: [
                        Container(
                          width: 48,
                          height: 48,
                          decoration: BoxDecoration(
                            color: AppColors.surface,
                            shape: BoxShape.circle,
                            border: Border.all(color: AppColors.primary, width: 2),
                          ),
                          child: ClipOval(
                            child: Image.asset(
                              'teams/${_selectedRace!.id}/logo.png',
                              fit: BoxFit.cover,
                              errorBuilder: (_, __, ___) => Icon(
                                PhosphorIcons.shield(PhosphorIconsStyle.fill),
                                color: AppColors.textMuted,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                _selectedRace!.name,
                                style: TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.bold,
                                  color: AppColors.textPrimary,
                                ),
                              ),
                              Row(
                                children: [
                                  _buildTierBadge(_selectedRace!.tier ?? 2),
                                  const SizedBox(width: 8),
                                  Text(
                                    'RR ${_selectedRace!.rerollCost ~/ 1000}k',
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: AppColors.textSecondary,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
        // Team name input
        TextField(
          decoration: InputDecoration(
            labelText: 'Nombre del equipo',
            hintText: 'ej: Los Leones de Altdorf',
            prefixIcon: Icon(PhosphorIcons.flag(PhosphorIconsStyle.bold)),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
          onChanged: (v) => setState(() => _teamName = v),
        ),
        const SizedBox(height: 24),
        Text(
          'SELECCIONA UNA RAZA',
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: AppColors.textMuted,
            letterSpacing: 1,
          ),
        ),
        const SizedBox(height: 16),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: isWide ? 6 : 3,
            childAspectRatio: 1.0,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
          ),
          itemCount: races.length,
          itemBuilder: (context, index) {
            final race = races[index];
            return RaceCard(
              race: race,
              isSelected: _selectedRace?.id == race.id,
              onTap: () => _selectRace(race),
            );
          },
        ),
      ],
    );
  }

  Widget _buildTierBadge(int tier) {
    final colors = {
      1: AppColors.success,
      2: AppColors.accent,
      3: AppColors.warning,
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: (colors[tier] ?? AppColors.textMuted).withOpacity(0.2),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        'Tier $tier',
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.bold,
          color: colors[tier] ?? AppColors.textMuted,
        ),
      ),
    );
  }

  Widget _buildRosterStep(bool isWide) {
    if (_loadingRaceDetail) {
      return const Center(child: CircularProgressIndicator());
    }

    final race = _selectedRace;
    final positions = race?.positions ?? <BasePosition>[];
    final rerollCost = race?.rerollCost ?? 50000;

    // ── Cabecera banner ──────────────────────────────────────────────────────
    Widget buildHeader() {
      if (race == null) return const SizedBox.shrink();
      return Container(
        height: 320,
        width: double.infinity,
        clipBehavior: Clip.hardEdge,
        decoration: const BoxDecoration(),
        child: Stack(
          clipBehavior: Clip.none,
          children: [
            // Fondo oscuro base
            Container(color: AppColors.background),
            // Wallpaper/personajes emergiendo desde la derecha
            Positioned(
              right: -20,
              top: -30,
              bottom: -20,
              child: Image.asset(
                'assets/teams/${race.id}/wallpaper.png',
                fit: BoxFit.contain,
                errorBuilder: (_, __, ___) => const SizedBox.shrink(),
              ),
            ),
            // Degradado lateral para fusionar el personaje con el fondo
            Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.centerLeft,
                  end: Alignment.centerRight,
                  stops: const [0.0, 0.45, 0.75, 1.0],
                  colors: [
                    AppColors.background,
                    AppColors.background.withOpacity(0.6),
                    AppColors.background.withOpacity(0.1),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
            // Degradado inferior para fundir con el contenido
            Positioned(
              bottom: 0,
              left: 0,
              right: 0,
              child: Container(
                height: 80,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Colors.transparent,
                      AppColors.background,
                    ],
                  ),
                ),
              ),
            ),
            // Info card top-left
            Positioned(
              top: 20,
              left: 24,
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.card.withOpacity(0.85),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: AppColors.surfaceLight),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(6),
                      child: Image.asset(
                        'assets/teams/${race.id}/logo.png',
                        width: 36,
                        height: 36,
                        errorBuilder: (_, __, ___) => Container(
                          width: 36,
                          height: 36,
                          decoration: BoxDecoration(
                            color: AppColors.primary.withOpacity(0.3),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Icon(PhosphorIcons.shield(PhosphorIconsStyle.fill),
                              color: AppColors.primary, size: 20),
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          race.name,
                          style: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(height: 3),
                        Row(
                          children: [
                            _buildTierBadge(race.tier ?? 2),
                            const SizedBox(width: 8),
                            Text(
                              'RR ${rerollCost ~/ 1000}k',
                              style: TextStyle(
                                fontSize: 11,
                                color: AppColors.textMuted,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            // Nombre del equipo grande centrado/izquierda
            Positioned(
              left: 24,
              right: 200,
              bottom: 24,
              child: Text(
                (_teamName.isNotEmpty ? _teamName : race.name).toUpperCase(),
                style: TextStyle(
                  fontFamily: 'Teko',
                  fontSize: 52,
                  fontWeight: FontWeight.w600,
                  color: Colors.white,
                  letterSpacing: 2,
                  height: 1,
                  shadows: [
                    Shadow(
                      color: Colors.black.withOpacity(0.8),
                      blurRadius: 12,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      );
    }

    // ── Tabla de reclutamiento ────────────────────────────────────────────────
    Widget buildRecruitmentTable() {
      return Container(
        decoration: BoxDecoration(
          color: AppColors.card,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.surfaceLight),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Cabecera de tabla
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: Row(
                children: [
                  Expanded(
                    flex: 5,
                    child: Text(
                      'RECLUTAMIENTO DE JUGADORES',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textPrimary,
                        letterSpacing: 0.5,
                      ),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: (_rosterCount >= 11 ? AppColors.success : AppColors.warning)
                          .withOpacity(0.15),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: _rosterCount >= 11 ? AppColors.success : AppColors.warning,
                        width: 0.5,
                      ),
                    ),
                    child: Text(
                      'Jugadores:  $_rosterCount / 16',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: _rosterCount >= 11 ? AppColors.success : AppColors.warning,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            // Cabecera de columnas
            Container(
              color: AppColors.surfaceLight.withOpacity(0.5),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: [
                  const SizedBox(width: 8),
                  _tableHeader('POSICIÓN', flex: 4),
                  _tableHeader('MA', flex: 1, center: true),
                  _tableHeader('ST', flex: 1, center: true),
                  _tableHeader('AG', flex: 1, center: true),
                  _tableHeader('PA', flex: 1, center: true),
                  _tableHeader('AV', flex: 1, center: true),
                  _tableHeader('HABILIDADES', flex: 5),
                  _tableHeader('COSTE', flex: 2, center: true),
                  _tableHeader('LÍMITE / CANTIDAD', flex: 4, center: true),
                ],
              ),
            ),
            // Filas de posiciones
            if (positions.isEmpty)
              Padding(
                padding: const EdgeInsets.all(32),
                child: Center(
                  child: Text(
                    'No hay posiciones disponibles',
                    style: TextStyle(color: AppColors.textMuted),
                  ),
                ),
              )
            else
              ...positions.map((pos) => _buildPositionRow(pos)),
          ],
        ),
      );
    }

    // ── Panel izquierdo: identidad del equipo ─────────────────────────────────
    Widget buildIdentityPanel() {
      return Container(
        decoration: BoxDecoration(
          color: AppColors.card,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.surfaceLight),
        ),
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Presupuesto
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              margin: const EdgeInsets.only(bottom: 16),
              decoration: BoxDecoration(
                color: AppColors.background,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: _remaining < 0 ? AppColors.error : AppColors.surfaceLight,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    PhosphorIcons.coinVertical(PhosphorIconsStyle.fill),
                    size: 16,
                    color: _remaining < 0 ? AppColors.error : AppColors.accent,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'PRESUPUESTO',
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textMuted,
                            letterSpacing: 1,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${_remaining ~/ 1000}k restantes',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: _remaining < 0 ? AppColors.error : AppColors.textPrimary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Text(
                    '${_spent ~/ 1000}k / ${_startingBudget ~/ 1000}k',
                    style: TextStyle(
                      fontSize: 11,
                      color: AppColors.textMuted,
                    ),
                  ),
                ],
              ),
            ),
            Text(
              'IDENTIDAD DEL EQUIPO',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                color: AppColors.textMuted,
                letterSpacing: 1,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Nombre del Equipo',
              style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
            ),
            const SizedBox(height: 6),
            TextField(
              controller: TextEditingController(text: _teamName)
                ..selection = TextSelection.collapsed(offset: _teamName.length),
              style: TextStyle(color: AppColors.textPrimary, fontSize: 14),
              decoration: InputDecoration(
                hintText: 'Ej. Gouged Eye',
                hintStyle: TextStyle(color: AppColors.textMuted),
                isDense: true,
                contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(color: AppColors.surfaceLight),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(color: AppColors.surfaceLight),
                ),
              ),
              onChanged: (v) => setState(() => _teamName = v),
            ),
            const SizedBox(height: 16),
            // Reglas especiales
            if (race != null && race.specialRules.isNotEmpty) ...[
              Text(
                'REGLAS ESPECIALES',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textMuted,
                  letterSpacing: 1,
                ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 6,
                runSpacing: 6,
                children: race.specialRules.map((rule) => Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: AppColors.primary.withOpacity(0.4)),
                  ),
                  child: Text(
                    rule,
                    style: TextStyle(
                      fontSize: 11,
                      color: AppColors.primary,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                )).toList(),
              ),
              const SizedBox(height: 16),
            ],
          ],
        ),
      );
    }

    // ── Panel de staff ────────────────────────────────────────────────────────
    Widget buildStaffPanel() {
      return Container(
        decoration: BoxDecoration(
          color: AppColors.card,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.surfaceLight),
        ),
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'EQUIPO TÉCNICO Y MEJORAS',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
                color: AppColors.textMuted,
                letterSpacing: 1,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                // Re-rolls
                Expanded(
                  child: _buildStaffTile(
                    icon: PhosphorIcons.arrowsClockwise(PhosphorIconsStyle.fill),
                    label: 'REROLLS',
                    subtitle: '${rerollCost ~/ 1000}k c/u',
                    count: _rerolls,
                    onDec: _rerolls > 0 ? () => setState(() => _rerolls--) : null,
                    onInc: _remaining >= rerollCost ? () => setState(() => _rerolls++) : null,
                  ),
                ),
                const SizedBox(width: 12),
                // Boticario
                Expanded(
                  child: _buildApothecaryTile(
                    allowed: race?.apothecaryAllowed ?? true,
                    enabled: _apothecary,
                    canToggle: !_apothecary ? _remaining >= 50000 : true,
                    onToggle: (v) => setState(() => _apothecary = v),
                  ),
                ),
                const SizedBox(width: 12),
                // Animadoras
                Expanded(
                  child: _buildStaffTile(
                    icon: PhosphorIcons.megaphone(PhosphorIconsStyle.fill),
                    label: 'ANIMADORAS',
                    subtitle: '10k c/u',
                    count: _cheerleaders,
                    onDec: _cheerleaders > 0 ? () => setState(() => _cheerleaders--) : null,
                    onInc: _remaining >= 10000 ? () => setState(() => _cheerleaders++) : null,
                  ),
                ),
                const SizedBox(width: 12),
                // Asistentes
                Expanded(
                  child: _buildStaffTile(
                    icon: PhosphorIcons.chalkboardTeacher(PhosphorIconsStyle.fill),
                    label: 'ASISTENTES',
                    subtitle: '10k c/u',
                    count: _assistantCoaches,
                    onDec: _assistantCoaches > 0 ? () => setState(() => _assistantCoaches--) : null,
                    onInc: _remaining >= 10000 ? () => setState(() => _assistantCoaches++) : null,
                  ),
                ),
              ],
            ),
          ],
        ),
      );
    }

    // ── Estado del roster ─────────────────────────────────────────────────────
    Widget buildRosterStatus() {
      final isValid = _rosterCount >= 11 && _remaining >= 0;
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isValid
              ? AppColors.success.withOpacity(0.08)
              : AppColors.warning.withOpacity(0.08),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isValid ? AppColors.success : AppColors.warning,
            width: 0.5,
          ),
        ),
        child: Row(
          children: [
            Icon(
              isValid
                  ? PhosphorIcons.checkCircle(PhosphorIconsStyle.fill)
                  : PhosphorIcons.warning(PhosphorIconsStyle.fill),
              color: isValid ? AppColors.success : AppColors.warning,
              size: 20,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isValid ? 'Roster Válido' : 'Roster Incompleto',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: isValid ? AppColors.success : AppColors.warning,
                    ),
                  ),
                  Text(
                    isValid
                        ? 'Cumples con el mínimo de 11 jugadores y no superas el presupuesto.'
                        : 'Necesitas al menos 11 jugadores (tienes $_rosterCount).',
                    style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                  ),
                ],
              ),
            ),
          ],
        ),
      );
    }

    // ── Layout completo ───────────────────────────────────────────────────────
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        buildHeader(),
        Padding(
          padding: const EdgeInsets.fromLTRB(32, 24, 32, 32),
          child: isWide
              ? Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Columna izquierda: identidad
                    SizedBox(
                      width: 280,
                      child: Column(
                        children: [
                          buildIdentityPanel(),
                        ],
                      ),
                    ),
                    const SizedBox(width: 20),
                    // Columna derecha: tabla + staff + estado
                    Expanded(
                      child: Column(
                        children: [
                          buildRecruitmentTable(),
                          const SizedBox(height: 16),
                          buildStaffPanel(),
                          const SizedBox(height: 16),
                          buildRosterStatus(),
                        ],
                      ),
                    ),
                  ],
                )
              : Column(
                  children: [
                    buildIdentityPanel(),
                    const SizedBox(height: 16),
                    buildRecruitmentTable(),
                    const SizedBox(height: 16),
                    buildStaffPanel(),
                    const SizedBox(height: 16),
                    buildRosterStatus(),
                  ],
                ),
        ),
      ],
    );
  }

  Widget _tableHeader(String text, {int flex = 1, bool center = false}) {
    return Expanded(
      flex: flex,
      child: Text(
        text,
        textAlign: center ? TextAlign.center : TextAlign.left,
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.bold,
          color: AppColors.textMuted,
          letterSpacing: 0.5,
        ),
      ),
    );
  }

  Widget _buildPositionRow(BasePosition pos) {
    final hired = _roster.where((r) => r.position.id == pos.id).length;
    final canHire = hired < pos.maxQuantity &&
        _remaining >= pos.cost &&
        _rosterCount < 16;
    final isMaxed = hired >= pos.maxQuantity;

    String _statCell(int val) => '$val';

    final perkNames = pos.startingPerks.map((p) => p.name).join(', ');

    return Container(
      decoration: BoxDecoration(
        border: Border(top: BorderSide(color: AppColors.surfaceLight, width: 0.5)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      child: Row(
        children: [
          // Indicador de estado
          Container(
            width: 6,
            height: 6,
            margin: const EdgeInsets.only(right: 10),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isMaxed
                  ? AppColors.textMuted.withOpacity(0.3)
                  : canHire
                      ? AppColors.success
                      : AppColors.warning,
            ),
          ),
          // Nombre posición
          Expanded(
            flex: 4,
            child: Text(
              pos.name,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: isMaxed ? AppColors.textMuted : AppColors.textPrimary,
              ),
            ),
          ),
          // Stats
          _statBadge(_statCell(pos.stats.ma), highlight: !isMaxed),
          _statBadge(_statCell(pos.stats.st), highlight: !isMaxed),
          _statBadge('${pos.stats.ag}+', highlight: !isMaxed),
          _statBadge(pos.stats.pa == 0 ? '-' : '${pos.stats.pa}+', highlight: !isMaxed),
          _statBadge('${pos.stats.av}+', highlight: !isMaxed),
          // Habilidades
          Expanded(
            flex: 5,
            child: Text(
              perkNames,
              style: TextStyle(
                fontSize: 11,
                color: AppColors.textSecondary,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          // Coste
          Expanded(
            flex: 2,
            child: Text(
              '${pos.cost ~/ 1000}k',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.bold,
                color: AppColors.accent,
              ),
            ),
          ),
          // Controles cantidad
          Expanded(
            flex: 4,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _circleButton(
                  icon: PhosphorIcons.minus(PhosphorIconsStyle.bold),
                  onTap: hired > 0
                      ? () {
                          final idx = _roster.lastIndexWhere((r) => r.position.id == pos.id);
                          if (idx >= 0) setState(() => _roster.removeAt(idx));
                        }
                      : null,
                ),
                const SizedBox(width: 8),
                Text(
                  '$hired',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: hired > 0 ? AppColors.textPrimary : AppColors.textMuted,
                  ),
                ),
                const SizedBox(width: 8),
                _circleButton(
                  icon: PhosphorIcons.plus(PhosphorIconsStyle.bold),
                  onTap: canHire ? () => _hirePlayer(pos) : null,
                ),
                const SizedBox(width: 8),
                Text(
                  '/ ${pos.maxQuantity}',
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.textMuted,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _statBadge(String val, {bool highlight = true}) {
    return Expanded(
      flex: 1,
      child: Center(
        child: Container(
          width: 32,
          height: 24,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: highlight
                ? AppColors.surfaceLight.withOpacity(0.7)
                : Colors.transparent,
            borderRadius: BorderRadius.circular(4),
          ),
          child: Text(
            val,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: highlight ? AppColors.textPrimary : AppColors.textMuted,
            ),
          ),
        ),
      ),
    );
  }

  Widget _circleButton({required IconData icon, VoidCallback? onTap}) {
    final enabled = onTap != null;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 26,
        height: 26,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: enabled ? AppColors.surfaceLight : AppColors.surfaceLight.withOpacity(0.3),
          border: Border.all(
            color: enabled ? AppColors.textSecondary : AppColors.textMuted.withOpacity(0.2),
          ),
        ),
        child: Icon(
          icon,
          size: 12,
          color: enabled ? AppColors.textPrimary : AppColors.textMuted.withOpacity(0.3),
        ),
      ),
    );
  }

  Widget _buildStaffTile({
    required IconData icon,
    required String label,
    required String subtitle,
    required int count,
    VoidCallback? onDec,
    VoidCallback? onInc,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppColors.surfaceLight),
      ),
      child: Column(
        children: [
          Icon(icon, color: AppColors.accent, size: 22),
          const SizedBox(height: 6),
          Text(label,
              style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textMuted,
                  letterSpacing: 0.5)),
          Text(subtitle,
              style: TextStyle(fontSize: 10, color: AppColors.textMuted)),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _circleButton(
                  icon: PhosphorIcons.minus(PhosphorIconsStyle.bold),
                  onTap: onDec),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 10),
                child: Text(
                  '$count',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: count > 0 ? AppColors.textPrimary : AppColors.textMuted,
                  ),
                ),
              ),
              _circleButton(
                  icon: PhosphorIcons.plus(PhosphorIconsStyle.bold),
                  onTap: onInc),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildApothecaryTile({
    required bool allowed,
    required bool enabled,
    required bool canToggle,
    required ValueChanged<bool> onToggle,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: enabled ? AppColors.success.withOpacity(0.5) : AppColors.surfaceLight,
        ),
      ),
      child: Column(
        children: [
          Icon(
            PhosphorIcons.firstAidKit(PhosphorIconsStyle.fill),
            color: allowed ? AppColors.accent : AppColors.textMuted,
            size: 22,
          ),
          const SizedBox(height: 6),
          Text(
            'BOTICARIO',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              color: AppColors.textMuted,
              letterSpacing: 0.5,
            ),
          ),
          Text(
            allowed ? '50k (Max 1)' : 'No disponible',
            style: TextStyle(fontSize: 10, color: AppColors.textMuted),
          ),
          const SizedBox(height: 8),
          Switch(
            value: enabled && allowed,
            onChanged: allowed && canToggle ? onToggle : null,
            activeColor: AppColors.success,
            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
          ),
        ],
      ),
    );
  }

  Widget _buildRecruitedPlayer(int index, _RecruitedPlayer player) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.card,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.surfaceLight),
      ),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: AppColors.surfaceLight,
              borderRadius: BorderRadius.circular(6),
            ),
            child: Center(
              child: Text(
                '#${index + 1}',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  player.position.name,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary,
                  ),
                ),
                Text(
                  '${player.position.cost ~/ 1000}k',
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.textMuted,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            icon: Icon(PhosphorIcons.trash(PhosphorIconsStyle.bold)),
            onPressed: () => setState(() => _roster.removeAt(index)),
            color: AppColors.error,
            iconSize: 18,
          ),
        ],
      ),
    );
  }

  Widget _buildStaffStep(bool isWide) {
    final rerollCost = _selectedRace?.rerollCost ?? 50000;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'PERSONAL Y EQUIPO',
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: AppColors.textMuted,
            letterSpacing: 1,
          ),
        ),
        const SizedBox(height: 16),
        // Re-rolls
        _buildStaffItem(
          icon: PhosphorIcons.arrowsClockwise(PhosphorIconsStyle.fill),
          label: 'Re-rolls',
          description: '${rerollCost ~/ 1000}k cada uno',
          count: _rerolls,
          maxCount: 8,
          cost: rerollCost,
          onIncrement: _remaining >= rerollCost
              ? () => setState(() => _rerolls++)
              : null,
          onDecrement: _rerolls > 0 ? () => setState(() => _rerolls--) : null,
        ),
        // Apothecary
        _buildStaffToggle(
          icon: PhosphorIcons.firstAidKit(PhosphorIconsStyle.fill),
          label: 'Apotecario',
          description: '50k',
          enabled: _apothecary,
          cost: 50000,
          canToggle: !_apothecary ? _remaining >= 50000 : true,
          onToggle: (v) => setState(() => _apothecary = v),
        ),
        // Assistant coaches
        _buildStaffItem(
          icon: PhosphorIcons.chalkboardTeacher(PhosphorIconsStyle.fill),
          label: 'Asistentes',
          description: '10k cada uno',
          count: _assistantCoaches,
          maxCount: 6,
          cost: 10000,
          onIncrement: _remaining >= 10000
              ? () => setState(() => _assistantCoaches++)
              : null,
          onDecrement: _assistantCoaches > 0
              ? () => setState(() => _assistantCoaches--)
              : null,
        ),
        // Cheerleaders
        _buildStaffItem(
          icon: PhosphorIcons.megaphone(PhosphorIconsStyle.fill),
          label: 'Animadoras',
          description: '10k cada una',
          count: _cheerleaders,
          maxCount: 12,
          cost: 10000,
          onIncrement: _remaining >= 10000
              ? () => setState(() => _cheerleaders++)
              : null,
          onDecrement:
              _cheerleaders > 0 ? () => setState(() => _cheerleaders--) : null,
        ),
        const SizedBox(height: 24),
        // Recommendations
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppColors.info.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: AppColors.info.withOpacity(0.3)),
          ),
          child: Row(
            children: [
              Icon(PhosphorIcons.lightbulb(PhosphorIconsStyle.fill),
                  color: AppColors.info, size: 20),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Se recomienda empezar con al menos 3 re-rolls y un apotecario para equipos que lo permitan.',
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.info,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildStaffItem({
    required IconData icon,
    required String label,
    required String description,
    required int count,
    required int maxCount,
    required int cost,
    VoidCallback? onIncrement,
    VoidCallback? onDecrement,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.card,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.surfaceLight),
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: AppColors.surfaceLight,
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: AppColors.accent, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary,
                  ),
                ),
                Text(
                  description,
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.textMuted,
                  ),
                ),
              ],
            ),
          ),
          Row(
            children: [
              IconButton(
                icon: Icon(PhosphorIcons.minus(PhosphorIconsStyle.bold)),
                onPressed: onDecrement,
                color: onDecrement != null
                    ? AppColors.textPrimary
                    : AppColors.textMuted,
              ),
              Container(
                width: 40,
                alignment: Alignment.center,
                child: Text(
                  '$count',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: count > 0 ? AppColors.accent : AppColors.textMuted,
                  ),
                ),
              ),
              IconButton(
                icon: Icon(PhosphorIcons.plus(PhosphorIconsStyle.bold)),
                onPressed: count < maxCount ? onIncrement : null,
                color: onIncrement != null && count < maxCount
                    ? AppColors.textPrimary
                    : AppColors.textMuted,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStaffToggle({
    required IconData icon,
    required String label,
    required String description,
    required bool enabled,
    required int cost,
    required bool canToggle,
    required ValueChanged<bool> onToggle,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.card,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: enabled ? AppColors.success : AppColors.surfaceLight,
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: AppColors.surfaceLight,
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: AppColors.accent, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary,
                  ),
                ),
                Text(
                  description,
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.textMuted,
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: enabled,
            onChanged: canToggle ? onToggle : null,
            activeThumbColor: AppColors.success,
          ),
        ],
      ),
    );
  }

  Widget _buildConfirmStep(bool isWide) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Team summary card
        Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: AppColors.card,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.accent.withOpacity(0.5)),
          ),
          child: Column(
            children: [
              // Team emblem
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: AppColors.surfaceLight,
                  shape: BoxShape.circle,
                  border: Border.all(color: AppColors.accent, width: 2),
                ),
                child: ClipOval(
                  child: Image.asset(
                    'teams/${_selectedRace?.id}/logo.png',
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => Icon(
                      PhosphorIcons.shield(PhosphorIconsStyle.fill),
                      size: 40,
                      color: AppColors.textMuted,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Text(
                _teamName.isEmpty ? 'Sin nombre' : _teamName,
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
                textAlign: TextAlign.center,
              ),
              Text(
                _selectedRace?.name ?? '',
                style: TextStyle(
                  fontSize: 14,
                  color: AppColors.textSecondary,
                ),
              ),
              const SizedBox(height: 24),
              const Divider(),
              const SizedBox(height: 16),
              // Stats
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildSummaryItem('Jugadores', '$_rosterCount'),
                  _buildSummaryItem('Re-rolls', '$_rerolls'),
                  _buildSummaryItem('Apotecario', _apothecary ? 'Sí' : 'No'),
                ],
              ),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(
                    child: Column(
                      children: [
                        Text(
                          'VALOR DEL EQUIPO',
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textMuted,
                            letterSpacing: 1,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${_spent ~/ 1000}k',
                          style: TextStyle(
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                            color: AppColors.accent,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Expanded(
                    child: Column(
                      children: [
                        Text(
                          'TESORERÍA',
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textMuted,
                            letterSpacing: 1,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${_remaining ~/ 1000}k',
                          style: TextStyle(
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                            color: AppColors.success,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),
        // Warnings
        if (!_isValidRoster)
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.error.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppColors.error.withOpacity(0.3)),
            ),
            child: Row(
              children: [
                Icon(PhosphorIcons.warning(PhosphorIconsStyle.fill),
                    color: AppColors.error, size: 20),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'El equipo necesita al menos 11 jugadores para poder jugar.',
                    style: TextStyle(
                      fontSize: 13,
                      color: AppColors.error,
                    ),
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildSummaryItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: AppColors.textPrimary,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: AppColors.textMuted,
          ),
        ),
      ],
    );
  }

  Widget _buildNavigationButtons() {
    final canProceed = _canProceed();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border(
          top: BorderSide(color: AppColors.surfaceLight),
        ),
      ),
      child: Row(
        children: [
          if (_currentStep > 0)
            Expanded(
              child: OutlinedButton(
                onPressed: () => setState(() => _currentStep--),
                child: const Text('Anterior'),
              ),
            )
          else
            const Spacer(),
          const SizedBox(width: 16),
          Expanded(
            child: ElevatedButton(
              onPressed: canProceed
                  ? () {
                      if (_currentStep < 3) {
                        setState(() => _currentStep++);
                      } else {
                        _createTeam();
                      }
                    }
                  : null,
              child: Text(_currentStep < 3 ? 'Siguiente' : 'Crear Equipo'),
            ),
          ),
        ],
      ),
    );
  }

  bool _canProceed() {
    switch (_currentStep) {
      case 0:
        return _teamName.isNotEmpty && _selectedRace != null;
      case 1:
        return _rosterCount >= 11;
      case 2:
        return true;
      case 3:
        return _isValidRoster;
      default:
        return false;
    }
  }

  void _hirePlayer(BasePosition position) {
    setState(() {
      _roster.add(_RecruitedPlayer(position: position));
    });
  }

  void _showExitDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppColors.surface,
        title: Text('¿Abandonar creación?',
            style: TextStyle(color: AppColors.textPrimary)),
        content: Text(
          'Se perderán todos los datos del equipo.',
          style: TextStyle(color: AppColors.textSecondary),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              context.go('/dashboard');
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.error,
            ),
            child: const Text('Salir'),
          ),
        ],
      ),
    );
  }

  void _createTeam() {
    // TODO: Submit team to API
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Equipo "$_teamName" creado correctamente'),
        backgroundColor: AppColors.success,
      ),
    );
    context.go('/dashboard');
  }
}

class _RecruitedPlayer {
  final BasePosition position;

  _RecruitedPlayer({required this.position});
}

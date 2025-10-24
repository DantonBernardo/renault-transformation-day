<?php

/**
 * Configurações de tempo para o sistema de detecção de cubos
 * Altere estes valores para ajustar os tempos médios esperados
 */

return [
    
    // ===========================================
    // CONFIGURAÇÕES DE TEMPO MÉDIO
    // ===========================================
    
    // Tempo médio esperado por cubo individual (em segundos)
    'expected_cube_time' => 5.0,
    
    // Tempo médio esperado por grupo (sempre 3x o tempo individual)
    'expected_group_time' => 15.0, // Será calculado como expected_cube_time * 3
    
    // Margem de tolerância para análise de desempenho (em segundos)
    'tolerance' => 5.0,
    
    // ===========================================
    // CONFIGURAÇÕES DE NOTIFICAÇÕES
    // ===========================================
    
    // Limite para considerar grupo atrasado (em segundos)
    // Deve ser menor que expected_group_time + tolerance
    'delayed_group_threshold' => 10.0,
    
    // Limite para considerar grupo adiantado (em segundos)  
    // Deve ser maior que expected_group_time - tolerance
    'early_group_threshold' => 2.0,
    
    // ===========================================
    // CONFIGURAÇÕES DE CACHE
    // ===========================================
    
    // Tempo de cache para grupos (em minutos)
    'groups_cache_time' => 1,
    
    // Tempo de cache para médias (em minutos)
    'averages_cache_time' => 5,
    
    // Tempo de cache para tempos recentes (em minutos)
    'latest_times_cache_time' => 0.5,
];

/**
 * Função helper para obter configurações de tempo
 */
function getTimingConfig($key = null) {
    $config = config('timing');
    
    // Garante que o tempo do grupo seja sempre 3x o tempo individual
    $config['expected_group_time'] = $config['expected_cube_time'] * 3;
    
    if ($key === null) {
        return $config;
    }
    
    return $config[$key] ?? null;
}

/**
 * Valida se as configurações estão consistentes
 */
function validateTimingConfig() {
    $config = getTimingConfig();
    
    $expectedGroupTime = $config['expected_group_time'];
    $tolerance = $config['tolerance'];
    $delayedThreshold = $config['delayed_group_threshold'];
    $earlyThreshold = $config['early_group_threshold'];
    
    $warnings = [];
    
    if ($delayedThreshold >= $expectedGroupTime + $tolerance) {
        $warnings[] = "delayed_group_threshold ({$delayedThreshold}s) deveria ser menor que expected_group_time + tolerance (" . ($expectedGroupTime + $tolerance) . "s)";
    }
    
    if ($earlyThreshold <= $expectedGroupTime - $tolerance) {
        $warnings[] = "early_group_threshold ({$earlyThreshold}s) deveria ser maior que expected_group_time - tolerance (" . ($expectedGroupTime - $tolerance) . "s)";
    }
    
    if ($expectedGroupTime != $config['expected_cube_time'] * 3) {
        $warnings[] = "expected_group_time ({$expectedGroupTime}s) deveria ser 3x expected_cube_time (" . ($config['expected_cube_time'] * 3) . "s)";
    }
    
    if (!empty($warnings)) {
        \Log::warning('Configurações de tempo inconsistentes: ' . implode('; ', $warnings));
    }
    
    return $warnings;
}

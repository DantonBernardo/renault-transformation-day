<?php

/**
 * Server-Sent Events para notificações em tempo real
 */

// Configuração de headers para SSE
header('Content-Type: text/event-stream');
header('Cache-Control: no-cache');
header('Connection: keep-alive');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Headers: Cache-Control');

// Função para enviar evento SSE
function sendSSE($data, $event = 'message') {
    echo "event: $event\n";
    echo "data: " . json_encode($data) . "\n\n";
    ob_flush();
    flush();
}

// Função para verificar se há novos dados
function checkForNewData($lastCheck) {
    // Verifica se há novos grupos desde a última verificação
    $groups = \App\Models\GroupOfThree::where('created_at', '>', $lastCheck)->count();
    return $groups > 0;
}

// Função para obter dados atualizados
function getUpdatedData() {
    $groups = \App\Models\GroupOfThree::with(['cubes' => function($query) {
        $query->select('id', 'group_id', 'color', 'face', 'individual_time');
    }])
    ->select('id', 'group_time', 'created_at')
    ->orderBy('created_at', 'desc')
    ->take(5)
    ->get();

    $averages = \App\Models\Cube::selectRaw('color, AVG(individual_time) as average_individual_time')
        ->groupBy('color')
        ->pluck('average_individual_time', 'color')
        ->toArray();

    $latestTimes = \App\Models\GroupOfThree::select('id', 'group_time', 'created_at')
        ->orderBy('created_at', 'desc')
        ->take(7)
        ->get();

    $notifications = [];
    $allGroups = \App\Models\GroupOfThree::with('cubes')->orderBy('created_at', 'desc')->get();
    
    foreach ($allGroups as $group) {
        $delayedThreshold = getTimingConfig('delayed_group_threshold');
        $earlyThreshold = getTimingConfig('early_group_threshold');
        
        if ($group->group_time > $delayedThreshold) {
            $maxCube = $group->cubes->sortByDesc('individual_time')->first();
            $diff = ($group->group_time) - $delayedThreshold;
            
            $notifications[] = [
                'type' => 'high_time',
                'message' => 'Grupo com tempo acima do esperado.',
                'group_id' => $group->id,
                'group_time' => $group->group_time,
                'cube' => [
                    'id' => $maxCube->id,
                    'color' => $maxCube->color,
                    'face' => $maxCube->face,
                    'individual_time' => $maxCube->individual_time,
                    'diff' => $diff
                ]
            ];
        } elseif ($group->group_time < $earlyThreshold) {
            $minCube = $group->cubes->sortBy('individual_time')->first();
            $diff = $earlyThreshold - $group->group_time;
            
            $notifications[] = [
                'type' => 'low_time',
                'message' => 'Grupo com tempo abaixo do esperado.',
                'group_id' => $group->id,
                'group_time' => $group->group_time,
                'cube' => [
                    'id' => $minCube->id,
                    'color' => $minCube->color,
                    'face' => $minCube->face,
                    'individual_time' => $minCube->individual_time,
                    'diff' => $diff
                ]
            ];
        }
    }

    return [
        'groups' => $groups,
        'averages' => $averages,
        'latestTimes' => $latestTimes,
        'notifications' => $notifications,
        'timestamp' => now()->toISOString()
    ];
}

// Loop principal do SSE
$lastCheck = now()->subMinutes(1); // Verifica dados dos últimos minutos

while (true) {
    // Verifica se a conexão ainda está ativa
    if (connection_aborted()) {
        break;
    }

    // Verifica se há novos dados
    if (checkForNewData($lastCheck)) {
        $data = getUpdatedData();
        sendSSE($data, 'data-update');
        $lastCheck = now();
    }

    // Envia heartbeat a cada 30 segundos
    sendSSE(['type' => 'heartbeat', 'timestamp' => now()->toISOString()], 'heartbeat');
    
    // Aguarda 2 segundos antes da próxima verificação
    sleep(2);
}

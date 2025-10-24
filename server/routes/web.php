<?php

use Illuminate\Support\Facades\Route;

// Rota para Server-Sent Events
Route::get('/sse', function () {
    return response()->stream(function () {
        // Inclui o arquivo SSE
        include base_path('routes/sse.php');
    }, 200, [
        'Content-Type' => 'text/event-stream',
        'Cache-Control' => 'no-cache',
        'Connection' => 'keep-alive',
        'Access-Control-Allow-Origin' => '*',
        'Access-Control-Allow-Headers' => 'Cache-Control',
    ]);
});

<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('cubes', function (Blueprint $table) {
            $table->index('color');
            $table->index('group_id');
            $table->index(['color', 'individual_time']);
        });

        Schema::table('group_of_three', function (Blueprint $table) {
            $table->index('created_at');
            $table->index(['created_at', 'group_time']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('cubes', function (Blueprint $table) {
            $table->dropIndex(['color']);
            $table->dropIndex(['group_id']);
            $table->dropIndex(['color', 'individual_time']);
        });

        Schema::table('group_of_three', function (Blueprint $table) {
            $table->dropIndex(['created_at']);
            $table->dropIndex(['created_at', 'group_time']);
        });
    }
};

<?php

use Illuminate\Support\Facades\Route;

use App\Http\Middleware\AlreadyLoggedIn;


/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
*/
Route::post('/api/v1/login', 'LoginController@login');

Route::get('/logout', 'LoginController@logout');

Route::get('/view', 'PDFController@index');

Route::get('/download', 'PDFController@download');

Route::get('/', 'HomeController@index');

Route::get('/login', function () {
    return view('home');
})->middleware(AlreadyLoggedIn::class);

Route::get('{any}', function () { 
    return view('home'); 
})->where('any', '.*'); 
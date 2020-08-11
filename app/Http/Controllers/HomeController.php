<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Http\Middleware\AlexAuthenticate;

class HomeController extends Controller
{
    public function __construct()
    {
        $this->middleware(AlexAuthenticate::class);
    }

    public function index()
    {
        return view('home');
    }
}

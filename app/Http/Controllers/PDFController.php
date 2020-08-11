<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Http\Middleware\AlexAuthenticate;

class PDFController extends Controller
{
    public function __construct()
    {
        $this->middleware(AlexAuthenticate::class);
    }


    public function index()
    {
        $pathToFile = storage_path().'/app/pdf/Abschlusszeitung2020.pdf';

        return response()->file(
            $pathToFile,
            ['Content-Type' => 'application/pdf']
        );
    }

    public function download()
    {
        $pathToFile = storage_path().'/app/pdf/Abschlusszeitung2020.pdf';

        return response()->download(
            $pathToFile,
            'Abschlusszeitung2020.pdf',
            ['Content-Type' => 'application/pdf']
        );
    }
}

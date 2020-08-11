<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Collection;

class LoginController extends Controller
{
    public function login(Request $request)
    {
        $collection = collect($request->all());
        $password = $collection->get('password');

        $hashedPasswords = [ // Earlier Line = Higher Priority = Faster Response
            '$2y$10$rM7RZHYP6NSRVZhGEhMFheC07CogCUu3TzNRAMMUZDBjL.wuSpdeO',
            '$2y$10$XkeW/1KKIc5W.LKIB.t/M.VhNbLd.078EdFsn8OtCdq9PJXGbLbP.'
        ];

        function checkPasswords($password, $hashedPasswords)
        {
            foreach ($hashedPasswords as $hashedPassword) {
                if (Hash::check($password, $hashedPassword)) {
                    return true;
                }
            }
            return false;
        }

        if (checkPasswords($password, $hashedPasswords)) {
            $request->session()->put('login', true);

            $response['data']['success'] = true;
        } else {
            $response['data']['success'] = false;
            $response['error']['type'] = "WRONG PASSWORD";
        }

        return response($response)->header('Content-Type', 'application/vnd.api+json');
    }

    public function logout(Request $request)
    {
        $request->session()->put('login', false);

        return redirect('/login');
    }
}

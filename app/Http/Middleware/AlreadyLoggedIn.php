<?php

namespace App\Http\Middleware;

use Closure;

class AlreadyLoggedIn
{
    /**
     * Handle an incoming request.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \Closure  $next
     * @return mixed
     */
    public function handle($request, Closure $next)
    {
        if ($request->session()->get('login') === true) {
            return redirect('/');
        } else {
            return $next($request);
        }
    }
}

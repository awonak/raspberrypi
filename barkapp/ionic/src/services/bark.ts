import { Injectable } from '@angular/core';
import { Http, Response } from '@angular/http';
import { Observable } from 'rxjs/Observable';


@Injectable()
export class BarkService {
  private allEndpoint = '/api/barks';
  private lastEndpoint = '/api/barks/last';

  constructor(private http: Http) { }

  all(): Observable<Response> {
    return this.http.get(this.allEndpoint);
  }

  last(): Observable<Response> {
    return this.http.get(this.lastEndpoint);
  }
}

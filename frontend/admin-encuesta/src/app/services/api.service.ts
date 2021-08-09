import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import urljoin from "url-join";
import { CookieService } from 'ngx-cookie-service';
import { environment } from "../../environments/environment";

@Injectable()
export class APIService {

    private apiUrl = environment.apiUrl;
    private headers;

    constructor(private http: HttpClient,
        private cookieService: CookieService) {
        let csrftoken = this.cookieService.get('csrftoken');
        if (csrftoken) {
            this.headers = {headers: {"X-CSRFToken": csrftoken }};
        }
    }

    public get(id: number):Observable<any> {
        return this.http.get(urljoin(this.apiUrl, 'encuesta/', id.toString(), '/preguntas'));
    }

    public create(data: any) {
        return this.http.post(urljoin(this.apiUrl, 'pregunta/'), data, this.headers);
    }

    public update(id: string, data: FormData){
        return this.http.patch(urljoin(this.apiUrl, 'pregunta/', id, '/'), data, this.headers);
    }

    public delete(id: number):Observable<any> {
        return this.http.delete(urljoin(this.apiUrl, 'pregunta', id.toString()), this.headers);
    }

    public deleteOpcion(id: number): Observable<any> {
        return this.http.delete(urljoin(this.apiUrl, 'opcion_pregunta', id.toString()), this.headers);
    }

    public setPreguntasOrder(encuesta: number, order: number[]): Observable<any> {
        let data = {
            encuesta: encuesta,
            order: order
        };
        return this.http.post(urljoin(this.apiUrl, 'set_preguntas_order'), data, this.headers);
    }

}
import { Injectable } from "@angular/core";
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import urljoin from "url-join";
import { CookieService } from 'ngx-cookie-service';
import { environment } from "../../environments/environment";



export enum Model {
    Segment = 'segment',
    LiveStream = 'livestream',
    SegmentSection = 'segmentsection',
    Question = 'question',
    Option = 'option',
    Slide = 'slide',
    DownloadableDocument = 'downloadabledocument',
    Forum = 'forum',
    Tarea = 'tarea'
}


@Injectable()
export class CoursesAPIService {

    private apiUrl = environment.apiUrl;
    private headers;

    constructor(private http: HttpClient,
        private cookieService: CookieService) {
        let csrftoken = cookieService.get('csrftoken');
        if (csrftoken) {
            this.headers = {headers: {"X-CSRFToken": csrftoken}};
        }
    }

    public httpGet(path: string): Observable<any> {
        return this.http.get(urljoin(this.apiUrl, path));
    }

    public httpPost(path: string, body?: any): Observable<any> {
        return this.http.post(urljoin(this.apiUrl, path), body, this.headers);
    }

    public get(type: string, id: number):Observable<any> {
        return this.http.get(urljoin(this.apiUrl, type.toLocaleLowerCase(), id.toString(), '/'));
    }

    public update(type: string, id: string, formData: FormData | {}){
        return this.http.patch(urljoin(this.apiUrl, type.toLocaleLowerCase(), id + '/'), formData, this.headers);
    }

    public create(type: string, formData: FormData | {}) {
        return this.http.post(urljoin(this.apiUrl, type.toLocaleLowerCase(), '/'), formData, this.headers);
    }

    public createWithProgress(type: string, formData: FormData | {}) {
        return this.http.post(urljoin(this.apiUrl, type.toLocaleLowerCase(), '/'), formData, {
            headers: this.headers.headers,
            reportProgress: true,
            observe: 'events'
        });
    }

    public delete(type: string, id: number):Observable<any> {
        return this.http.delete(urljoin(this.apiUrl, type.toLocaleLowerCase(), id.toString(), '/'), this.headers);
    }

    public segment_order(course_id: number): Observable<any> {
        return this.http.get(urljoin(this.apiUrl, 'course_segments/', course_id.toString()));
    }

    public live_streams_order(course_id: number): Observable<any> {
        return this.http.get(urljoin(this.apiUrl, 'course_live_streams/', course_id.toString()));
    }

    public segment_section_order(segment_id: number): Observable<any> {
        return this.http.get(urljoin(this.apiUrl, 'segment_sections/', segment_id.toString()));
    }

    public forum_order(course_id: number): Observable<any> {
        return this.http.get(urljoin(this.apiUrl, 'forums/', course_id.toString()));
    }

    public start_streaming(segment_id: number): Observable<any> {
        return this.httpPost(urljoin(Model.LiveStream.toLocaleLowerCase(), segment_id.toString(), 'start_streaming/'));
    }

    public stop_streaming(segment_id: number): Observable<any> {
        return this.httpPost(urljoin(Model.LiveStream.toLocaleLowerCase(), segment_id.toString(), 'stop_streaming/'));
    }
}

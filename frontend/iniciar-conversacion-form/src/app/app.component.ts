import { Component, ViewEncapsulation, Input, OnInit } from '@angular/core';
import * as _ from 'lodash';

@Component({
  selector: 'iniciar-conversacion-form',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class AppComponent implements OnInit {
  
  @Input() config: string;

  public showType: boolean = false;
  public showTutor: boolean = false;
  public showAdmin: boolean = false;
  public showStudent: boolean = false;
  public inputSendAs: string;
  public configObj: any;
  public autocomplete_users: any;
  public autocomplete_courses: any;

  public selected_areas: Array<Object>;
  public selected_domains: Array<Object>;
  public selected_users: Array<Object>;
  public selected_courses: Array<Object>;

  public selected_areas_ids: Array<number> = [];
  public selected_domains_ids: Array<number> = [];
  public selected_users_ids: Array<number> = [];
  public selected_courses_ids: Array<number> = [];

  public ngOnInit(): void {
    this.configObj = JSON.parse(this.config);
    if (this.configObj.isAdmin) {
      this.showType = true;
      this.setSendAs('Admin');
    } else if (this.configObj.isTutor) {
      this.showType = true;
      this.setSendAs('Tutor');
    } else {
      this.setSendAs('Alumno');
    }
    if(this.configObj.preSelect) {
      this.setSendAs('Alumno');
    }
  }

  public setSendAs(type: string) {
    this.showAdmin = type == 'Admin';
    this.showTutor = type == 'Tutor';
    this.showStudent = type == 'Alumno';
    this.inputSendAs = type;
    if (type == 'Tutor') {
      this.autocomplete_users = this.configObj.tutorUsers;
      this.autocomplete_courses = this.configObj.tutorCourses;
    }
    if (type == 'Admin') {
      this.autocomplete_users = this.configObj.allUsers;
      this.autocomplete_courses = this.configObj.allCourses;
    }
    
  }

  public getCoursesWithTutor() {
    if (this.configObj.myCourses) {
      return this.configObj.myCourses.filter(c => c.tutor);
    }
  }

  public getCourseOptions() {
    if(this.showAdmin) {
      return this.configObj.allCourses;
    } else if(this.showTutor) {
      return this.configObj.tutorCourses;
    } else if(this.showStudent) {
      return this.configObj.myCourses;
    }
  }

  public addToInput(input: Array<any>, event: any, attr = 'id') {
    input.push(event[attr]);
  }

  public removeFromInput(input: Array<any>, event: any, attr = 'id'){
      _.remove(input, (elem => elem == event[attr]));
  }

}
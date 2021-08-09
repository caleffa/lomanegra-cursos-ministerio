import { Component, ViewEncapsulation, ViewChild, Input } from '@angular/core';
import { CoursesAPIService } from '../../services/api.service';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import {LiveStreamComponent} from "../live-stream/live-stream.component";

// Force rebuild

@Component({
    selector: 'edit-live-stream',
    templateUrl: './edit-live-stream.component.html',
    styleUrls: ['./edit-live-stream.component.scss'],
    encapsulation: ViewEncapsulation.None
})
export class EditLiveStreamComponent {
    @ViewChild('spinnerModal', {static: false}) protected spinnerModal;

    @ViewChild('liveStreamComp', {static: false}) private liveStreamComp: LiveStreamComponent;

    @Input() course_id: number;
    @Input() segment_id: number;

    public constructor(public apiService: CoursesAPIService,
        private modalService: NgbModal) {
    }

    private getComponent() {
        return this.liveStreamComp;
    }

    public load() {
        let component = this.getComponent();
        component.load(this.segment_id, this.course_id);
    }
}
